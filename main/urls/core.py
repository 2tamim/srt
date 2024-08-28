from django.urls import path, include, re_path
from ..views import core

app_name = 'core'

urlpatterns = [
    path('login/', core.user_login, name='login'),
    path('logout/', core.user_logout, name='logout'),
    path('', core.dashboard, name='home'),
    path('project/', core.projects_home, name='project_home'),
    path('project/<int:project_id>/', core.projects_single, name='project_single'),
    path('project/graph/<int:project_id>/', core.projects_graph, name='projects_graph'),
    path('project/add/', core.add_project, name='add_project'),
    path('map/<str:mission>', core.project_map, name='map'),
    path('map-access/<str:mission>', core.project_map_access, name='map_access'),
]
