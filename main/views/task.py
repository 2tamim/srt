from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from ..models import Task, TaskStep
from django.contrib import messages
from django.db.models import Q
import datetime


@login_required(login_url='core:login')
def home(request):
    if request.method == 'GET':
        User = get_user_model()
        users = User.objects.all()

        usr = User.objects.get(id=request.user.id)
        tasks = Task.objects.filter(assignee=usr)

        context = {'tasks': tasks, 'users': users}

        return render(request, 'main/task/home.html', context)

    if request.method == 'POST':
        task_status_start = request.POST.get('task_status_start')
        task_status_done = request.POST.get('task_status_done')

        if task_status_start:
            if Task.objects.filter(id=task_status_start, status=0).exists():
                Task.objects.filter(id=task_status_start).update(status=1)

        elif task_status_done:
            if Task.objects.filter(id=task_status_done, status=1).exists():
                Task.objects.filter(id=task_status_done).update(status=2)


        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'access/'))


@login_required(login_url='core:login')
def projects_activity(request):
    # try:
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        task_assignee = request.POST.get('task_assignee')
        task_description = request.POST.get('task_description')
        task_start_time = datetime.datetime.strptime(request.POST.get('task_start_time'), '%Y-%m-%dT%H:%M').replace(
            tzinfo=datetime.timezone.utc)
        task_finish_time = datetime.datetime.strptime(request.POST.get('task_finish_time'), '%Y-%m-%dT%H:%M').replace(
            tzinfo=datetime.timezone.utc)
        task_step = request.POST.getlist('task_step')

        User = get_user_model()
        usr = User.objects.get(id=task_assignee)

        t = Task.objects.create(name=task_name, description=task_description, creator=request.user, assignee=usr,
                            start_time=task_start_time, finish_time=task_finish_time, type=2
                            )

        for i in range(len(task_step)):
            if task_step[i]:
                TaskStep.objects.create(task=t, title=task_step[i])

        messages.success(request, 'This task add successfully!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'task/activity/'))
    messages.warning(request, 'This task already exist!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'task/activity/'))

    # except:
    #     return render(request, 'main/core/projects/home.html')


@login_required(login_url='core:login')
def projects_activity_single(request):
    # try:
    return render(request, 'main/task/activity/single.html')

# except:
#     return render(request, 'main/core/projects/home.html')
