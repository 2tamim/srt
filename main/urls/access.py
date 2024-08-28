from django.urls import path, include, re_path
from ..views import access

app_name = 'access'

urlpatterns = [
    path('', access.home, name='home'),
    path('<int:acc_id>/', access.single, name='single'),
    path('edit/<int:acc_id>/', access.edit, name='edit'),
    path('add/', access.add, name='add'),
    path('assign/<int:acc_id>/', access.assign_user_access, name='assign'),
    ]