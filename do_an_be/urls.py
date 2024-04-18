
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
     path('api/v1/user/', include('user.urls')),
     path('api/v1/knowledge/', include('knowledge.urls')),
     path('api/v1/src_code/', include('src_code.urls')),
     path('api/v1/article/', include('article.urls')),
    path('api/v1/post/', include('post.urls')),
]


urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
