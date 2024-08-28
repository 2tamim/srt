from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import Project, Scan, Network, IP, Domain, SubDomain, Service, Web, Technology, AdditionalScreenshot, Product, Vulnerability, VulnerableProduct, AttackVector
import datetime
from distutils.version import LooseVersion
from django.contrib import messages
from django.http import HttpResponseRedirect


@login_required(login_url='core:login')
def reco(request,scan_id):
    if request.user.is_superuser or request.user.extension.access == 2 :
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()

    scan = Scan.objects.get(id = scan_id)
    products = Product.objects.all()
    if scan.project in projects:
        context = {"scan": scan,"products": products}
        return render(request, 'main/scan/reco.html', context)
    else:
        return redirect('core:project_home')
    

@login_required(login_url='core:login')
def add_reco(request):
    if request.user.is_superuser or request.user.extension.access == 2 :
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()

    try:
        project = projects.get(id = int(request.POST.get('project_id')))
        name = request.POST.get('scan_name')
        if len(request.POST.get('scan_start_date')) > 0 :
            start_date = datetime.datetime.strptime(request.POST.get('scan_start_date'), '%Y-%m-%dT%H:%M').replace(tzinfo=datetime.timezone.utc)
        else:
            start_date = None

        if len(request.POST.get('scan_done_date')) > 0 :
            done_date = datetime.datetime.strptime(request.POST.get('scan_done_date'), '%Y-%m-%dT%H:%M').replace(tzinfo=datetime.timezone.utc)
        else:
            done_date = None

        scan = Scan.objects.create(project=project, name=name, user=request.user,
                                       start_date=start_date, done_date=done_date)

        messages.success(request, 'Scan added successfully!')
    except Exception as Ex:
        messages.error(request, 'Error Adding Scan! ' + str(Ex))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))

@login_required(login_url='core:login')
def add_network(request):
    if request.user.is_superuser or request.user.extension.access == 2 :
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()

    # try:
    project = projects.get(id = int(request.POST.get('project_id')))
    if project:
        cidr = request.POST.get('network_cidr')
        if len(request.POST.get('network_record')) > 0:
            network_record = request.POST.get('network_record')
        else:
            network_record = None
        if len(request.POST.get('network_netname')) > 0:
            net_name = request.POST.get('network_netname')
        else:
            net_name = None
        if len(request.POST.get('network_registerer')) > 0:
            registerer = request.POST.get('network_registerer')
        else:
            registerer = None
        if len(request.POST.get('network_country')) > 1:
            country = request.POST.get('network_country')
        else:
            country = None

        Scans = Scan.objects.filter(id__in = [int(x) for x in request.POST.getlist('network_scans')])

        network = Network.objects.create(user=request.user, cidr=cidr, network_record=network_record,
                                        net_name=net_name, registerer=registerer, country=country)
        network.scans.set(Scans)
        network.projects.add(project)
    messages.success(request, 'Network added successfully!')
    # except Exception as Ex:
    #     messages.error(request, 'Error Adding Network! ' + str(Ex))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))


@login_required(login_url='core:login')
def add_ip(request):
    if request.user.is_superuser or request.user.extension.access == 2 :
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()

    networks = Network.objects.filter(id = -1)

    for project in projects:
        networks |= project.networks.all()
    try:
        network = Network.objects.get(id = int(request.POST.get('ip_network')))
        if network in networks :
            ip = request.POST.get('ip_ip')
            if len(request.POST.get('ip_name')) > 0 :
                name = request.POST.get('ip_name')
            else :
                name = None

            Scans = Scan.objects.filter(id__in = [int(x) for x in request.POST.getlist('ip_scans')])
            ip = IP.objects.create(network=network, name=name, user=request.user, ip=ip)

            ip.scans.set(Scans)
            messages.success(request, 'IP added successfully!')

        else:
            messages.error(request, 'Access forbiden for selected network')
    except Exception as Ex:
        messages.error(request, 'Error Adding Network! ' + str(Ex))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))


@login_required(login_url='core:login')
def add_domain(request):
    if request.user.is_superuser or request.user.extension.access == 2 :
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()

    try:
        project = projects.get(id = int(request.POST.get('project_id')))
        if project:
            name = request.POST.get('domain_name')
            status = request.POST.get('domain_status')
            if len(request.POST.get('domain_description'))>0:
                description = request.POST.get('domain_description')
            else:
                description = None
            if len(request.POST.get('domain_whois')) > 0:
                whois = request.POST.get('domain_whois')
            else:
                whois = None
            if len(request.POST.get('domain_registerer')) > 0:
                registerer = request.POST.get('domain_registerer')
            else:
                registerer = None
            if len(request.POST.get('domain_email')) > 0:
                email = request.POST.get('domain_email')
            else:
                email = None
            if len(request.POST.get('domain_phone')) > 0:
                phone = request.POST.get('domain_phone')
            else:
                phone = None
            if len(request.POST.get('domain_address')) > 0:
                address = request.POST.get('domain_address')
            else:
                address = None
            if request.POST.get('domain_country') != '0':
                country = request.POST.get('domain_country')
            else:
                country = None
            if len(request.POST.get('domain_city')) > 0:
                city = request.POST.get('domain_city')
            else:
                city = None

            try:
                expire = datetime.datetime.strptime(request.POST.get('domain_expire'), '%Y-%m-%dT%H:%M').replace(tzinfo=datetime.timezone.utc)
            except:
                expire = None

            ips = IP.objects.filter(id__in = [int(x) for x in request.POST.getlist('domain_ips')])
            Scans = Scan.objects.filter(id__in = [int(x) for x in request.POST.getlist('domain_scans')])

            domain = Domain.objects.create(name=name, user=request.user, status=status, project=project,
                                        description=description, whois=whois, registerer=registerer,
                                        email=email, phone=phone, address=address, country=country, city=city,
                                        expire=expire)
            domain.ips.set(ips)
            domain.scans.set(Scans)
            domain.save()

            messages.success(request, 'Domain added successfully!')
        else:
            messages.error(request, 'Access forbiden for selected project')
    except Exception as Ex:
        messages.error(request, 'Error Adding Network! ' + str(Ex))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))


@login_required(login_url='core:login')
def add_subdomain(request):
    if request.user.is_superuser or request.user.extension.access == 2:
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()

    # try:
    domain = Domain.objects.get(id=int(request.POST.get('subdomain_domain')))
    if domain.project in projects:
        name = request.POST.get('subdomain_name')
        web = Web.objects.get(id=int(request.POST.get('subdomain_web')))
        if not (domain.project in web.service.ip.network.projects):
            messages.error(request, 'Web and Domain not for same project')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))

        if len(request.POST.get('subdomain_description')) > 0:
            description = request.POST.get('subdomain_description')
        else:
            description = None

        if 'subdomain_exists' in request.POST:
            exists = True
        else:
            exists = False

        if request.POST.get('subdomain_ip') != '0':
            ip = IP.objects.get(id = int(request.POST.get('subdomain_ip')))
        else:
            ip=None

        Scans = Scan.objects.filter(id__in = [int(x) for x in request.POST.getlist('subdomain_scans')])
        subdomain = SubDomain.objects.create(domain=domain, name=name, user=request.user,
                                            description=description, exists=exists, web = web, ip = ip)

        subdomain.scans.set(Scans)
        subdomain.save()

        messages.success(request, 'Subdomain added successfully!')
    else:
        messages.error(request, 'Access forbiden for selected Domain')
    # except Exception as Ex:
    #     messages.error(request, 'Error Adding Web! ' + str(Ex))
    #
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))

@login_required(login_url='core:login')
def add_service(request):
    if request.user.is_superuser or request.user.extension.access == 2 :
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()

    networks = Network.objects.filter(id = -1)

    for project in projects:
        networks |= project.networks.all()

    try:
        ip = IP.objects.get(id = int(request.POST.get('service_ip')))
        if ip.network in networks :
            if len(request.POST.get('service_name')) > 0:
                name = request.POST.get('service_name')
            else:
                name = None
            port = int(request.POST.get('service_port'))
            protocol = request.POST.get('service_protocol')
            application = request.POST.get('service_application')

            if len(request.POST.get('service_description')) > 0 :
                description = request.POST.get('service_description')
            else:
                description = None

            if len(request.POST.get('service_version')) > 0:
                version = request.POST.get('service_version')
                LooseVersion(version)
            else:
                version = None
            
            Scans = Scan.objects.filter(id__in = [int(x) for x in request.POST.getlist('ip_scans')])

            service = Service.objects.create(ip=ip, name=name, user=request.user,
                 description=description, port=port, protocol=protocol, 
                 application=application, version=version)

            service.scans.set(Scans)

            messages.success(request, 'Service added successfully!')
        else:
            messages.error(request, 'Access forbiden for selected IP')
    except Exception as Ex:
        messages.error(request, 'Error Adding Service! ' + str(Ex))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))

@login_required(login_url='core:login')
def add_web(request):
    if request.user.is_superuser or request.user.extension.access == 2 :
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()
    networks = Network.objects.filter(id = -1)

    for project in projects:
        networks |= project.networks.all()

    try:
        service = Service.objects.get(id = int(request.POST.get('web_service')))

        if service.ip.network in networks :
            protocol = request.POST.get('web_protocol')
            status_code = request.POST.get('web_status')
            content_type = request.POST.get('web_content_type')
            content = request.POST.get('web_content')
            url = request.POST.get('web_url')
            try:
                name = request.POST.get('web_name')
            except:
                name = None
            try:
                screenshot = request.FILES.get('web_screenshot')
            except:
                screenshot = None

            Scans = Scan.objects.filter(id__in = [int(x) for x in request.POST.getlist('web_scans')])

            web = Web.objects.create(service=service, name=name, user=request.user,
                 url=url, screen_shot=screenshot, protocol=protocol, 
                 status_code=status_code, content_type=content_type,
                 content=content)

            web.scans.set(Scans)
            web.save()

            for scr_shot in request.FILES.getlist('web_screenshots'):
                AdditionalScreenshot.objects.create(web = web, screen_shot=scr_shot)

            messages.success(request, 'Web added successfully!')
        else:
            messages.error(request, 'Access forbiden for selected Service')
    except Exception as Ex:
        messages.error(request, 'Error Adding Web! ' + str(Ex))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))


@login_required(login_url='core:login')
def add_technology(request):
    if request.user.is_superuser or request.user.extension.access == 2 :
        projects = Project.objects.all()
    else:
        projects = request.user.authorized_projects.all()

    networks = Network.objects.filter(id = -1)

    for project in projects:
        networks |= project.networks.all()

    try:
        web = Web.objects.get(id = int(request.POST.get('tech_web')))

        if web.service.ip.network in networks :
            category  = request.POST.get('tech_category')
            name = request.POST.get('tech_name')

            try:
                version = request.POST.get('tech_version')
            except:
                version = None
            if version and len(version) > 0:
                LooseVersion(version)
            else:
                version = None

            try:
                product = Product.objects.get(id = int(request.POST.get('tech_product')))
            except:
                product = None
            
            Scans = Scan.objects.filter(id__in = [int(x) for x in request.POST.getlist('tech_scans')])
            technology = Technology.objects.create(web=web, name=name, user=request.user,
                                                    version=version, product=product)

            vulns = VulnerableProduct.objects.filter(product = product)
            for vuln in vulns :
                if vuln.from_version == '*' and vuln.to_version == '*':
                    if AttackVector.objects.filter(technology = technology, vulnerability = vuln.vulnerability).count() == 0:
                        AttackVector.objects.create(technology = technology, vulnerability = vuln.vulnerability, seen_time = None)
                elif vuln.from_version == '*' and LooseVersion(version) <= LooseVersion(vuln.to_version):
                    if AttackVector.objects.filter(technology = technology, vulnerability = vuln.vulnerability).count() == 0:
                        AttackVector.objects.create(technology = technology, vulnerability = vuln.vulnerability, seen_time = None)
                elif LooseVersion(vuln.from_version) <= LooseVersion(version) and vuln.to_version == '*' :
                    if AttackVector.objects.filter(technology = technology, vulnerability = vuln.vulnerability).count() == 0:
                        AttackVector.objects.create(technology = technology, vulnerability = vuln.vulnerability, seen_time = None)
                elif LooseVersion(vuln.from_version) <= LooseVersion(version) and LooseVersion(version) <= LooseVersion(vuln.to_version):
                    if AttackVector.objects.filter(technology = technology, vulnerability = vuln.vulnerability).count() == 0:
                        AttackVector.objects.create(technology = technology, vulnerability = vuln.vulnerability, seen_time = None)

            messages.success(request, 'Technology added successfully!')
        else:
            messages.error(request, 'Access forbiden for selected Web')
    except Exception as Ex:
        messages.error(request, 'Error Adding Technology! ' + str(Ex))

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))

def web(request):
    return render(request, 'main/scan/web/list.html')


def domain(request):
    return render(request, 'main/scan/domain/domain.html')


def subdomain(request):
    return render(request, 'main/scan/domain/subdomain.html')


def service(request):
    return render(request, 'main/scan/service/list.html')


def network(request):
    return render(request, 'main/scan/network/list.html')
