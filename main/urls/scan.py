from django.urls import path, include, re_path
from ..views import scan

app_name = 'scan'

urlpatterns = [
    path('reco/add/', scan.add_reco, name='add_reco'),
    path('reco/add/network', scan.add_network, name='add_network'),
    path('reco/add/ip', scan.add_ip, name='add_ip'),
    path('reco/add/domain', scan.add_domain, name='add_domain'),
    path('reco/add/sudomain', scan.add_subdomain, name='add_subdomain'),
    path('reco/add/web', scan.add_web, name='add_web'),
    path('reco/add/service', scan.add_service, name='add_service'),
    path('reco/add/technology', scan.add_technology, name='add_technology'),
    path('reco/<int:scan_id>/', scan.reco, name='reco'),
    path('web/', scan.web, name='web'),
    path('domain/', scan.domain, name='domain'),
    path('subdomain/', scan.subdomain, name='subdomain'),
    path('service/', scan.service, name='service'),
    path('network/', scan.network, name='network'),
]