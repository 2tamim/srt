from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from ..models import Access, Project, AccessType, PrivilegeLevel, Task
from django.contrib.auth.decorators import login_required
import datetime
from django.contrib.auth import get_user_model



@login_required(login_url='core:login')
def home(request):
    if request.user.is_superuser or request.user.extension.access == 2:
        accesses = Access.objects.all()
        projects = Project.objects.all()
        access_type = AccessType.objects.all()
        privilege_level = PrivilegeLevel.objects.all()
        User = get_user_model()
        users = User.objects.all()
        context = {'accesses': accesses, 'projects': projects, 'access_type': access_type, 'privilege_level': privilege_level,
                   'users':users
                   }
        return render(request, 'main/access/home.html', context)


@login_required(login_url='core:login')
def single(request, acc_id):
    # try:
        accesses = Access.objects.all()
        acc = accesses.get(id=acc_id)
        context = {'acc': acc}
        return render(request, 'main/access/single.html', context)
    # except:
    #     return render(request, 'main/access/home.html')


@login_required(login_url='core:login')
def edit(request, acc_id):
    # try:
    if request.method == 'GET':
        accesses = Access.objects.all()
        acc = accesses.get(id=acc_id)
        context = {'acc': acc}
        return render(request, 'main/access/edit.html', context)

    if request.method == 'POST':
        acc_valid = request.POST.get('acc_valid')
        acc_delivery = request.POST.get('acc_delivery')

        if acc_valid:
            if Access.objects.filter(id=acc_id).exists():
                Access.objects.filter(id=acc_id).update(valid=acc_valid)

        if acc_delivery:
            if Access.objects.filter(id=acc_id).exists():
                Access.objects.filter(id=acc_id).update(delivered=acc_delivery)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'access/'))


# except:
        # return render(request, 'main/access/home.html')


@login_required(login_url='core:login')
def add(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                if request.POST.get('acc_pro') == '0':
                    acc_pro = None
                else:
                    acc_pro = Project.objects.get(id = int(request.POST.get('acc_pro')))

                if len(request.POST.get('acc_title')) > 0:
                    acc_title = request.POST.get('acc_title')
                else:
                    acc_title = None

                if len(request.POST.get('acc_desc')) > 0:
                    acc_desc = request.POST.get('acc_desc')
                else:
                    acc_desc = None

                acc_type = request.POST.get('acc_type')
                acc_lvl = request.POST.get('acc_lvl')
                acc_address = request.POST.get('acc_address')
                acc_username = request.POST.get('acc_username')
                acc_password = request.POST.get('acc_password')
                if len(request.POST.get('acc_find')) > 0:
                    acc_find = datetime.datetime.strptime(request.POST.get('acc_find'), '%Y-%m-%dT%H:%M').replace(
                            tzinfo=datetime.timezone.utc)
                else:
                    acc_find = None

                if 'acc_valid' in request.POST:
                    acc_valid = True
                else:
                    acc_valid = False

                if 'acc_delivered' in request.POST:
                    acc_del = True
                else:
                    acc_del = False
                acc_target = request.POST.get('acc_delivered_to')

                Access.objects.create(title=acc_title, project=acc_pro,description=acc_desc,
                                    access_type_id=acc_type, priv_level_id=acc_lvl,
                                    user=request.user, valid= acc_valid,find_time=acc_find,
                                    address=acc_address,username=acc_username, password=acc_password,
                                    delivered=acc_del ,delivery_target=acc_target )

                messages.success(request, 'This Access add successfully!')
            except Exception as Ex:
                messages.error(request, 'Error Adding Access! ' + str(Ex))

            return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'access/'))
        messages.warning(request, 'This Access already exist!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'access/'))


@login_required(login_url='core:login')
def assign_user_access(request, acc_id):
    # try:
    if request.method == 'POST':
        acc_user = request.POST.get('acc_user')

        if acc_user:
            User = get_user_model()
            usr = User.objects.get(id=acc_user)

            if Access.objects.filter(id=acc_id).exists():
                Access.objects.filter(id=acc_id).update(assignee=usr)

                Task.objects.create(name='task_access_'+str(acc_id), creator=request.user, assignee=usr,
                                    status=1
                                    )

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'access/'))


# except:
        # return render(request, 'main/access/home.html')