from django.contrib import admin
from django.urls import path,include
from django.urls import re_path
from rest_framework.authtoken import views as authtoken_views
from . import views


urlpatterns = [
    path('get_all', views.get_article),
    path('get', views.api_get_article_details),
    path('get_knowledge_article', views.get_knowledge),
    path('get_by_knowledge_type', views.get_article_knowledge_type),
    path('like', views.article_like),
    path('unlike', views.article_unlike),
    path('comment', views.article_comment),
]
