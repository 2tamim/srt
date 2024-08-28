from django.urls import path, include, re_path
from ..views import projects

app_name = 'project'

urlpatterns = [
    path('', projects.home, name='home'),
    # path('single/', projects.single, name='single'),
    # path('edit/', projects.edit, name='edit'),
    ]