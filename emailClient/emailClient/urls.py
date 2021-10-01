"""emailClient URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from inbox import views as v
from login import views as l

urlpatterns = [
    path('inbox/', v.inbox),
    path('login/home', l.login),
    path('', l.login),
    path('admin/', admin.site.urls),
    path('login/', l.authentication, name='authentication'),
    path('login/<int:ID>', l.view, name='view')
    ]
