from django.urls import path, include, re_path
from ..views import task

app_name = 'task'

urlpatterns = [
    path('works/', task.home, name='home'),
    path('activity/', task.projects_activity, name='activity_list'),
    path('activity/single', task.projects_activity_single, name='activity_single'),

]
