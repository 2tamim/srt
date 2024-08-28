from django.urls import path, include, re_path
from ..views import vuln

app_name = 'vuln'

urlpatterns = [
    path('', vuln.home, name='home'),
    path('<int:vuln_id>/', vuln.single, name='single'),
    path('edit/<int:vuln_id>/', vuln.edit, name='edit'),
    path('add/', vuln.add, name='add'),
]
