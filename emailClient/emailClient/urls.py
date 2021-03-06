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
from login import views as l

urlpatterns = [
    path('logout/', l.logout),
    path('login/home', l.authentication),
    path('', l.authentication),
    path('admin/', admin.site.urls),
    path('login/', l.authentication, name='authentication'),
    path('message/<int:ID>', l.view, name='view'),
    path('forward/<int:ID>', l.forward, name='forward'),
    path('filter/', l.filter, name='filter'),
    path('attach/files/<str:filename>/', l.download),
    path('attach/<int:ID>', l.attach, name='attach'),
    path('send/', l.send, name='send'),
    path('trash/', l.trash),
    path('trash/<int:ID>', l.moveTrash),
    path('fromTrash/<int:ID>', l.fromTrash),
    path('delete/<int:ID>', l.delete),
    path('drafts/', l.drafts),
    path('draft/<int:ID>', l.draftCompose),
    path('inbox', l.inbox)
    ]
