from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.utils.functional import cached_property
from .fields import OrderField

# Create your models here.


####
####  Core 
####

class ProjectCategory(models.Model):
    """ProjectCategory Model"""
    name = models.CharField(max_length=64)
    avatar = models.ImageField(upload_to='avatar/projectcat/')


class ProjectArea(models.Model):
    """ProjectArea Model"""
    name = models.CharField(max_length=64)
    avatar = models.ImageField(upload_to='avatar/')


class Project(models.Model):
    """Project Model"""

    status_choices = (
        (0, 'To do'),
        (1, 'Doing'),
        (2, 'Done'),
        (3, 'Updating')
    )

    mission_choices = (
        (0, 'Mission'),
        (1, 'Non mission'),
        (2, 'Mission related')
    )

    name = models.CharField(max_length=2048, unique = True)
    area = models.ForeignKey(
        ProjectArea, on_delete=models.PROTECT, related_name='projects',blank=True, null=True)
    category = models.ForeignKey(
        ProjectCategory, on_delete=models.PROTECT, related_name='projects')
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(default=0, choices=status_choices)
    mission = models.IntegerField(default=0, choices=mission_choices)
    country = CountryField()
    progress = models.PositiveIntegerField(default=0)
    man_hour_cost = models.PositiveIntegerField(default=0)


    parent = models.ForeignKey(
        "self",blank=True, null=True, on_delete=models.PROTECT, related_name="subprojects")
    manager = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='managed_projects')
    authorized_users = models.ManyToManyField(
        User, blank=True, related_name='authorized_projects')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="projects")

    deadline = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    @cached_property
    def country_flag(self):
        return self.country.flag

    @cached_property
    def scan_count(self):
        return self.scans.all().count()
		
    @cached_property
    def status_text(self):
        return self.status_choices[self.status]

    @cached_property
    def attack_vectors(self):
        att_vec_list = AttackVector.objects.filter(id = -1)
        for network in self.networks.all():
            for ip in network.ips.all():
                for service in ip.services.all():
                    for web in service.web.all():
                        for technology in web.technologies.all():
                            att_vec_list |= technology.attack_vectors.all()
        return att_vec_list


class Notification(models.Model):
    """Notification Model"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications')
    time = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128, blank=False, null=False)
    message = models.TextField(blank=False, null= False)
    link = models.CharField(max_length=1024, blank=True, null=True)
    seen = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['time']


class UserExtension(models.Model):
    """UserExtension Model"""

    access_choices = (
        (0,'Intern'),
        (1,'Staff'),
        (2,'Admin')
    )

    user = models.OneToOneField(
        User, on_delete= models.CASCADE, related_name='extension')
    access = models.IntegerField(choices=access_choices, default=1)
    avatar = models.ImageField(upload_to='avatar/')
    

####
####  Vuln 
####

class ProductCategory(models.Model):
    """ProductCategory Model"""

    name = models.CharField(max_length=64)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']

class Product(models.Model):
    """Product Model"""

    name = models.CharField(max_length=128, unique=True)
    official_site = models.URLField(null=True, blank=True)
    icon = models.ImageField(upload_to="icon/")
    category = models.ForeignKey(
        ProductCategory, on_delete=models.PROTECT, related_name='products')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Vulnerability(models.Model):
    """Vulnerability Model"""

    severity_choices = (
        (0, 'Low'),
        (1, 'Medium'),
        (2, 'High'),
        (3, 'Critical')
    )

    auth_req_choices = (
        (0, 'None'),
        (1, 'Low'),
        (2, 'High'),
    )

    cve = models.CharField(max_length=16, unique=True)
    score = models.DecimalField(max_digits=4, decimal_places=2)
    severity = models.IntegerField(choices=severity_choices)
    vul_type = models.CharField(max_length=100)
    auth_req = models.IntegerField(choices=auth_req_choices)
    interaction_req = models.BooleanField()
    publish_date = models.DateField(blank=True, null=True)
    verified = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="vulns")

    description = models.TextField(blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    @cached_property
    def product_set(self):
        id_list = self.products.all().values_list('product__pk', flat = True)
        return Product.objects.filter(pk__in = id_list)

    @cached_property
    def has_poc(self):
        if self.vuln_files.filter(type = 1).count() + self.vuln_links.filter(type = 1).count() > 0:
            return True
        else:
            return False

    @cached_property
    def has_exp(self):
        if self.vuln_files.filter(type = 2).count() + self.vuln_links.filter(type = 2).count() > 0:
            return True
        else:
            return False

class VulnerableProduct(models.Model):
    """VulnerableProduct Model"""

    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name='vulnerabilties')
    edition = models.CharField(max_length=128, blank=True, null=True)
    from_version = models.CharField(max_length=16, default='1.0')
    to_version = models.CharField(max_length=16, default='1.0')

    vulnerability = models.ForeignKey(
        Vulnerability, on_delete=models.CASCADE, related_name='products')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['vulnerability','edition','product','from_version'], name='version_ranges'),]


class VulnerabilityFile(models.Model):
    """VulnerabilityFile Model"""

    def upload_path_handler(instance, type):
        return "vuln/vul_{id}_{type}".format(id=instance.vul.id, type=type)

    filetype_choices = (
        (0, 'Attachment'),
        (1, 'POC'),
        (2, 'EXP'),
        (3, 'Demo')
    )

    vul = models.ForeignKey(
        Vulnerability, on_delete=models.PROTECT, related_name='vuln_files')
    name = models.CharField(max_length=256, blank=True, null=True)
    type = models.IntegerField(choices=filetype_choices, default=0)
    vfile = models.FileField(upload_to=upload_path_handler)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="vuln_files")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    @cached_property
    def type_text(self):
        return self.filetype_choices[self.type]

class VulnerabilityLink(models.Model):
    """VulnerabilityLink Model"""

    linktype_choices = (
        (0, 'Description'),
        (1, 'POC'),
        (2, 'EXP')
    )

    vul = models.ForeignKey(
        Vulnerability, on_delete=models.PROTECT, related_name='vuln_links')
    name = models.CharField(max_length=256, blank=True, null=True)
    type = models.IntegerField(choices=linktype_choices, default=0)
    link = models.URLField()
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="vuln_links")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['vul','link'], name='vuln_link'),]

    @cached_property
    def type_text(self):
        return self.linktype_choices[self.type]


####
####  Scan 
####

class Scan(models.Model):
    """Scan Model"""


    name = models.CharField(max_length=2048)
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name='scans')

    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="scans")

    start_date = models.DateTimeField(blank=True,null=True)
    done_date = models.DateTimeField(blank=True,null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['name', 'project'], name='scan_project'),]

    @cached_property
    def domain_count(self):
        return self.domains.all().count()

    @cached_property
    def subdomain_count(self):
        count = 0
        for dom in self.domains.all():
            count += dom.subdomains.all().count()
        return count

    @cached_property
    def network_count(self):
        return self.networks.all().count()


class Network(models.Model):
    """Network Model"""

    cidr = models.CharField(max_length=100, unique=True)
    network_record = models.TextField(blank=True, null=True)
    net_name = models.CharField(max_length=200, blank=True, null=True)
    registerer = models.CharField(max_length=200, blank=True, null=True)
    country = CountryField(blank=True, null=True)


    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="networks", blank=True, null=True)
    projects = models.ManyToManyField(
        Project, related_name='networks')
    scans = models.ManyToManyField(
        Scan, related_name='networks')
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    @cached_property
    def ip_count(self):
        return self.ips.all().count()

    @cached_property
    def country_flag(self):
        return self.country.flag

    def l_ip(self):
        return 0

    def f_ip(self):
        return 0


class IP(models.Model):
    """IP Model"""
    ip = models.GenericIPAddressField(unique=True)
    name = models.CharField(max_length=1024, blank= True, null=True)
    
    network = models.ForeignKey(
        Network, on_delete=models.CASCADE, related_name='ips')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,null=True, blank=True, related_name="ips")
    scans = models.ManyToManyField(
        Scan, related_name='ips')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']


class Domain(models.Model):
    """Domain Model"""
    status_choices = (
        (0, 'Up'),
        (1, 'Down')
    )
    name = models.CharField(max_length=2048, unique=True)
    status = models.IntegerField(default=0, choices=status_choices)
    description = models.TextField(blank=True, null=True)
    whois = models.TextField( blank=True, null=True)
    registerer = models.CharField(max_length=2048, blank=True, null=True)
    email = models.CharField(max_length=2048, blank=True, null=True)
    phone = models.CharField(max_length=2048, blank=True, null=True)
    address = models.CharField(max_length=2048, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    city = models.CharField(max_length=256, blank=True, null=True)
    expire = models.DateTimeField(blank=True, null=True)
    
    ips = models.ManyToManyField(
        IP, related_name='domains')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,null=True, blank=True, related_name="domains")
    scans = models.ManyToManyField(
        Scan, related_name='domains')
    project = models.ForeignKey(
        Project, on_delete=models.PROTECT, related_name='domains')


    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']

    @cached_property
    def subdomain_count(self):
        return self.subdomains.all().count()


class Service(models.Model):
    """Service Model"""
    status_choices = (
        (0, 'Up'),
        (1, 'Filter'),
        (2, 'Down')
    )

    name = models.CharField(max_length=1024, blank=True, null=True)
    port = models.SmallIntegerField()
    status = models.SmallIntegerField(default=0, choices=status_choices)
    protocol = models.CharField(max_length=64)
    application = models.CharField(max_length=128)
    version = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    ip = models.ForeignKey(
        IP, on_delete=models.CASCADE, related_name='services')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,null=True, blank=True, related_name="services")
    scans = models.ManyToManyField(
        Scan, related_name='services')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['name', 'ip'], name='service_ip'),
            models.UniqueConstraint(fields=['port', 'ip'], name='service_ip_port'),]


class Web(models.Model):
    """Web Model"""

    name = models.CharField(max_length=1024, blank=True, null=True)
    url = models.CharField(max_length=2048, unique=True)
    protocol = models.CharField(max_length=64)
    screen_shot = models.FileField(blank=True, null=True)
    status_code = models.CharField(max_length=64)
    content_type = models.CharField(max_length=128)
    content = models.TextField()

    service = models.ForeignKey(
        Service, on_delete=models.PROTECT, related_name='web')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,null=True, blank=True, related_name="web")
    scans = models.ManyToManyField(
        Scan, related_name='webs')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']


class SubDomain(models.Model):
    """Subdomain Model"""
    name = models.CharField(max_length=2048)
    description = models.TextField(blank=True, null=True)
    exists = models.BooleanField(blank=True)

    ip = models.ForeignKey(
        IP, on_delete=models.SET_NULL,null=True, blank=True, related_name='subdomains')
    domain = models.ForeignKey(
        Domain, on_delete=models.CASCADE, related_name='subdomains')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,null=True, blank=True, related_name="subdomains")
    scans = models.ManyToManyField(
        Scan, related_name='subdomains')
    web = models.ForeignKey(
        Web, on_delete=models.PROTECT, related_name='subdomains')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['name', 'domain'], name='subdomain_domain'),]


class AdditionalScreenshot(models.Model):
    """AdditionalScreenshot Model"""

    web = models.ForeignKey(
        Web, on_delete = models.CASCADE, related_name='add_screenshots')
    screen_shot = models.FileField(blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']


class Technology(models.Model):
    """Technology Model"""

    name = models.CharField(max_length=128)
    version = models.CharField(max_length=64, blank=True, null=True)

    web = models.ForeignKey(
        Web, on_delete=models.CASCADE, related_name='technologies')
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, related_name='technologies', blank= True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.PROTECT,null=True, blank=True, related_name="technologies")
    scans = models.ManyToManyField(
        Scan, related_name='technologies')

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['product','version','web'], name='technology_product'),]


class AttackVector(models.Model):
    """AttackVector Model"""

    technology = models.ForeignKey(
        Technology, on_delete=models.PROTECT, related_name='attack_vectors')
    vulnerability = models.ForeignKey(
        Vulnerability, on_delete=models.PROTECT, related_name='attack_vectors')

    seen_time = models.DateTimeField(blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['technology','vulnerability'], name='att_vec_vunl_tech'),]

####
####  Access 
####

class AccessType(models.Model):
    ''' AccessType Model'''

    name = models.CharField(max_length=64)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']


class PrivilegeLevel(models.Model):
    ''' PrivilegeLevel Model'''
    
    importance_choices = (
        (0, 'Low'),
        (1, 'Normal'),
        (2, 'High'),
        (3, 'Very High'),
        (4, 'Critical')
    )

    name = models.CharField(max_length=64)
    admin = models.BooleanField(default=False)
    importance = models.PositiveSmallIntegerField(default=0, choices=importance_choices)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']


class Access(models.Model):
    ''' Access Model'''

    title = models.CharField(max_length=254, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='accesses', null=True, blank=True)
    access_type = models.ForeignKey(
        AccessType, on_delete=models.PROTECT, related_name='accesses')
    priv_level = models.ForeignKey(
        PrivilegeLevel, on_delete=models.PROTECT, related_name='accesses')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='accesses')
    assignee = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="assigned_access",blank=True, null=True)

    
    address = models.TextField()
    username = models.TextField()
    password = models.TextField()
    find_time = models.DateTimeField(blank=True, null=True)

    valid = models.BooleanField(default=False)

    delivered = models.BooleanField(default=False)
    delivery_target = models.CharField(max_length=256,blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']


class AccessComment(models.Model):
    ''' AccessComment Model'''

    access = models.ForeignKey(
        Access, on_delete=models.CASCADE, related_name="commnets")
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="access_comments")
    text = models.TextField()

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']


class AccessAttachment(models.Model):
    """AccessAttachment Model"""

    access = models.ForeignKey(
        Access, on_delete=models.CASCADE, related_name='attachments')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="access_attachments")
    afile = models.FileField(upload_to='task/')
    filename = models.CharField(max_length=256)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']


####
####  Task 
####

class Task(models.Model):
    """Task Model"""

    tasktype_choices = (
        (0, 'vul'),
        (1, 'acc'),
        (2, 'other'),
    )

    taskstatus_choices = (
        (0, 'assigned'),
        (1, 'doing'),
        (2, 'done'),
    )

    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)

    creator = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="created_tasks")
    assignee = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="assigned_tasks")

    seen_time = models.DateTimeField(blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    success_result = models.BooleanField(blank=True, null=True)
    final_report = models.TextField(blank=True, null=True)
    finish_time = models.DateTimeField(blank=True, null=True)

    type = models.IntegerField(choices=tasktype_choices, blank=True, null=True)
    status = models.IntegerField(choices=taskstatus_choices, default=0)

    result_confirmed = models.BooleanField(default=False)
    confirm_time = models.DateTimeField(blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']


class TaskComment(models.Model):
    """TaskComment Model"""

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="task_comments")
    text = models.TextField()

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']


class TaskStep(models.Model):
    """TaskStep Model"""

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='steps')
    title = models.CharField(max_length=256)
    order = OrderField(null=True, blank=True, for_fields=['task'])

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']




class TaskAttachment(models.Model):
    """TaskAttachment Model"""

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='attachments')
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="task_attachments")
    afile = models.FileField(upload_to='task/')
    filename = models.CharField(max_length=256)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']


class VulnVerification(models.Model):
    """VulnVerification Model"""

    task = models.OneToOneField(
        Task, on_delete=models.CASCADE, related_name='vuln_verification')
    vulnerability = models.ForeignKey(
        Vulnerability, on_delete=models.CASCADE, related_name="vuln_verifications")
    final = models.BooleanField(default=False)


class AccessCheck(models.Model):
    """VulnVerification Model"""

    task = models.OneToOneField(
        Task, on_delete=models.CASCADE, related_name='access_check')
    access = models.ForeignKey(
        Access, on_delete=models.CASCADE, related_name='access_checks')
    final = models.BooleanField(default=False)


class Activity(models.Model):
    """Activity Model"""

    task = models.OneToOneField(
        Task, on_delete=models.CASCADE, related_name='activity')
    attack_vector = models.ForeignKey(
        AttackVector, on_delete=models.CASCADE, blank=True, null=True, related_name='activities')
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE,related_name='activities')
    result_accesses = models.ManyToManyField(
        Access, related_name='causing_activities')
    
