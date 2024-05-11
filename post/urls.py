from django.urls import path
from . import views

urlpatterns =[
    path('add', views.create_post),
    path('get', views.get_post),
    path('like', views.post_like),
    path('unlike', views.post_unlike),
    path('comment', views.post_comment),
    path('update', views.update),
    path('delete', views.delete_post),
]