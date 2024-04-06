from django.contrib import admin
from django.urls import path,include
from django.urls import re_path
from rest_framework.authtoken import views as authtoken_views
from . import views

urlpatterns = [
    path('get_all_language', views.get_all_language),
    path('get_src_code', views.get_src_code),
]
