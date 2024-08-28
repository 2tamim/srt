from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls.core', namespace='core')),
    path('vuln/', include('main.urls.vuln', namespace='vuln')),
    path('access/', include('main.urls.access', namespace='access')),
    path('task/', include('main.urls.task', namespace='task')),
    path('scan/', include('main.urls.scan', namespace='scan')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)