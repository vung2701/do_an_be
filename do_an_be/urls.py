
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
     path('api/v1/user/', include('user.urls')),
     path('api/v1/knowledge/', include('knowledge.urls')),
     path('api/v1/src_code/', include('src_code.urls')),
     path('api/v1/article/', include('article.urls')),
]
