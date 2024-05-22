from django.contrib import admin
from django.urls import path,include
from django.urls import re_path
from rest_framework.authtoken import views as authtoken_views
from . import views


urlpatterns = [
    path('get', views.get_article),
    path('get_detail', views.api_get_article_details),
    path('knowledge', views.get_knowledge),
    path('like', views.article_like),
    path('unlike', views.article_unlike),
    path('comment', views.article_comment),
    path('spotlight', views.get_spotlight),
]
