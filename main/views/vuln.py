from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from ..models import Vulnerability, VulnerableProduct, VulnerabilityFile, Product, Technology, AttackVector, Project
from distutils.version import LooseVersion
import datetime



@login_required(login_url='core:login')
def home(request):
    try:
        products = Product.objects.all()
        vuln = Vulnerability.objects.all()
        vuln_files = VulnerabilityFile.objects.all()
        context = {'products': products, 'Vulnerabilities': vuln, 'vuln_files': vuln_files}
        return render(request, 'main/vuln/home.html', context)
    except:
        return render(request, 'main/vuln/home.html')


@login_required(login_url='core:login')
def single(request, vuln_id):
    try:
        vulnerability = Vulnerability.objects.all()
        vuln = vulnerability.get(id=vuln_id)
        vulnerabilityFile = VulnerabilityFile.objects.all()
        vuln_file = vulnerabilityFile.filter(vul=vuln)
        products = Product.objects.all()
        context = {'vuln': vuln, 'vuln_file':vuln_file, 'products': products}
        return render(request, 'main/vuln/single.html', context)
    except:
        return render(request, 'main/vuln/single.html')


@login_required(login_url='core:login')
def edit(request, vuln_id):
    try:
        vulnerability = Vulnerability.objects.all()
        vuln = vulnerability.get(id=vuln_id)

        if request.method == 'GET':
                vulnerabilityFile = VulnerabilityFile.objects.all()
                vuln_file = vulnerabilityFile.filter(vul=vuln)
                context = {'vuln': vuln, 'vuln_file':vuln_file}
                return render(request, 'main/vuln/edit.html', context)

        if request.method == 'POST':
            vul_verify = request.POST.get('vul_verify')
            vul_file_type = request.POST.get('vul_file_type')
            vul_file_ = request.FILES.get('vul_file_')

            if vul_verify:
                if Vulnerability.objects.filter(id=vuln_id).exists():
                    Vulnerability.objects.filter(id=vuln_id).update(verified=vul_verify)

            elif vul_file_:
                file = VulnerabilityFile()
                file.vul = vuln
                file.name = vul_file_.name
                file.type = vul_file_type
                file.vfile = vul_file_
                file.user = request.user
                file.save()

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))

    except:
        return render(request, 'main/vuln/home.html')


@login_required(login_url='core:login')
def add(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                vul_id = request.POST.get('vul_id')
                vul_score = request.POST.get('vul_score')
                vul_rate = request.POST.get('vul_rate')
                vul_type = request.POST.get('vul_type')
                vul_auth = request.POST.get('vul_auth')
                vul_verify = (request.POST.get('vul_verify') != None)
                vul_interaction = (request.POST.get('vul_interaction') != None)
                if len(request.POST.get('vul_publish')) > 0:
                    vul_publish = datetime.datetime.strptime(request.POST.get('vul_publish'), '%Y-%m-%dT%H:%M').replace(
                        tzinfo=datetime.timezone.utc)
                else:
                    vul_publish = None

                vul_files_poc = request.FILES.getlist('time_add_input_poc_')
                vul_files_exploit = request.FILES.getlist('time_add_input_exploit_')

                vul_description = request.POST.get('vul_description')

                v = Vulnerability.objects.create(cve=vul_id, score=vul_score, description = vul_description,
                                                severity=vul_rate, vul_type=vul_type, auth_req=vul_auth,
                                                interaction_req=vul_interaction, publish_date=vul_publish,
                                                verified=vul_verify, user=request.user)

                for i in range(len(request.POST.getlist('vul_from'))):
                    product = request.POST.getlist('vul_tech')[i]
                    from_version = request.POST.getlist('vul_from')[i]
                    LooseVersion(from_version)
                    to_version = request.POST.getlist('vul_to')[i]
                    if to_version == '':
                        to_version = from_version
                    else:
                        LooseVersion(to_version)
                    edition = request.POST.getlist('vul_edition')[i]
                    if edition =='':
                        edition = None

                    if LooseVersion(to_version)< LooseVersion(from_version):
                        messages.error(request, 'From version can`t be bigger than to version ! ' )
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))

                    VulnerableProduct.objects.create(vulnerability = v, edition = edition, product_id = product,
                                                    from_version = from_version, to_version = to_version)

                for i in vul_files_poc:
                    poc = VulnerabilityFile()
                    poc.vul = v
                    poc.name = i.name
                    poc.type = 1
                    poc.vfile = i
                    poc.user = request.user
                    poc.save()

                for i in vul_files_exploit:
                    exp = VulnerabilityFile()
                    exp.vul = v
                    exp.name = i.name
                    exp.type = 2
                    exp.vfile = i
                    exp.user = request.user
                    exp.save()

                # for tech in Technology.objects.filter(product = v.product):
                #     if v.versions.all().count() == 0 or tech.version:
                #         AttackVector.objects.create(technology = tech, vulnerability = v, seen_time = None)
                #     else:
                #         for ver in v.versions.all():
                #             if LooseVersion(ver.from_version) <= LooseVersion(tech.version) and LooseVersion(tech.version) <= LooseVersion(ver.to_version):
                #                 AttackVector.objects.create(technology = tech, vulnerability = v, seen_time = None)
                #                 break

                messages.success(request, 'This Vulnerability added successfully!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))
            except Exception as Ex:
                messages.error(request, 'Error Adding Vulnerability! ' + str(Ex))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))
        messages.warning(request, 'This Vulnerability already exist!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))


@login_required(login_url='core:login')
def add_product(request, vuln_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                v = Vulnerability.objects.get(id=vuln_id)
                for i in range(len(request.POST.getlist('vul_from'))):
                    product = request.POST.getlist('vul_tech')[i]
                    from_version = request.POST.getlist('vul_from')[i]
                    LooseVersion(from_version)
                    to_version = request.POST.getlist('vul_to')[i]
                    if to_version == '':
                        to_version = from_version
                    else:
                        LooseVersion(to_version)
                    edition = request.POST.getlist('vul_edition')[i]
                    if edition =='':
                        edition = None

                    if LooseVersion(to_version)< LooseVersion(from_version):
                        messages.error(request, 'From version can`t be bigger than to version ! ' )
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))

                    VulnerableProduct.objects.create(vulnerability = v, edition = edition, product_id = product,
                                                    from_version = from_version, to_version = to_version)

                messages.success(request, 'Products added successfully!')
            except Exception as Ex:
                messages.error(request, 'Error Adding Product! ' + str(Ex))

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'project/'))