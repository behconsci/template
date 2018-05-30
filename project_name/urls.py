from django.contrib import admin
from django.urls import path

from {{ project_name }}.apps.core.views import letsencrypt


urlpatterns = [
    path('.well-known/acme-challenge/pFmV21J6LJNm4q3E4H0rY6iUDjSjVJmLlSGCnPs3u0Y', letsencrypt),
    path('admin/', admin.site.urls),
]
