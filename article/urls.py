from django.contrib import admin
from django.urls import path,include
from django.urls import re_path
from rest_framework.authtoken import views as authtoken_views
from . import views


urlpatterns = [
    path('get_all', views.get_article),
    path('like', views.article_like),
    path('unlike', views.article_unlike),
    path('comment', views.article_comment),
]
