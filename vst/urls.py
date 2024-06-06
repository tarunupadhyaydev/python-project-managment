"""vst URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import re_path as url

# from employees.custom_admin import admin_site

# Adds site header, site title, index title to the admin side.
admin.site.site_header = 'VST Administrator'
admin.site.site_title = 'VSAT Administrator'
admin.site.index_title = 'VST Administrator'

urlpatterns = [
    path("", admin.site.urls),
    #url(r'^logout/$',  auth_views.LogoutView.as_view(), {'next_page': '/login'}),
    #path("logout/", lambda request: redirect("/admin/logout", permanent=False)),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    #path('admin/', admin_site.urls),
]
