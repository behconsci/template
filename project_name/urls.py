from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from {{ project_name }}.apps.core.views import letsencrypt, index


urlpatterns = [
    path('', index, name='index'),
    path('.well-known/acme-challenge/pFmV21J6LJNm4q3E4H0rY6iUDjSjVJmLlSGCnPs3u0Y', letsencrypt),

    path('user/', include('{{ project_name }}.apps.user.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
