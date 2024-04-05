
from django.contrib import admin
from django.urls import path,include
from django.urls import re_path
from rest_framework.authtoken import views as authtoken_views
from . import views

urlpatterns = [
    path('register', views.register),
    path('verify/<uidb64>', views.verify_email, name='user_verify_email'),
    path('get', views.get_user),
    # path('login', views.user_login, name='user_login'),
    path('login', authtoken_views.obtain_auth_token, name='user_login_obtain_auth_token'),
    path('logout', views.user_logout, name='user_logout'),
    path('my_profile/get', views.get_my_profile, name='user_get_my_profile'),
    path('profile/get', views.get_profile),
    path('profile/update', views.edit_profile, name='edit_profile'),
    path('upload_image', views.upload_user_image, name='upload_user_image'),
]
