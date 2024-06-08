
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from . import  sitemap_views
from django.contrib.sitemaps.views import sitemap


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^sitemap.xml$", sitemap_views.sitemapindex),
    re_path(r"^sitemap_index.xml$", sitemap_views.sitemapindex),
    re_path(r'^sitemap-(?P<section>.+)\.xml$', sitemap, {'sitemaps': sitemap_views.sitemaps}),
    
    path('api/v1/user/', include('user.urls')),
    path('api/v1/knowledge/', include('knowledge.urls')),
    path('api/v1/src_code/', include('src_code.urls')),
    path('api/v1/article/', include('article.urls')),
    path('api/v1/post/', include('post.urls')),
]


urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
