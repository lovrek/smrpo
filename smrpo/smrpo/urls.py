"""smrpo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from adminplus.sites import AdminSitePlus
from django.conf.urls import url, include, patterns
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from .views import index

admin.site = AdminSitePlus()
admin.autodiscover()

urlpatterns = [
    url(r'^$', index, name='home'),
    url(r'^faculties/', include('faculties.urls')),
    url(r'^study-programs/', include('study_programs.urls')),
    url(r'^information/', include('information.urls')),
    url(r'^accounts/', include('login.urls')),
    url(r'^application/', include('applications.urls')),
    url(r'^admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
