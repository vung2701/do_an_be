
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings

from do_an_be import views

from . import  sitemap_views
# from user import views as user_views
from django.contrib.auth import views as auth_views

from django.contrib.sitemaps.views import sitemap
from oauth2_provider.views import AuthorizationView, TokenView
from .views import MyProtectedView

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
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('accounts/login/', views.login_view, name='login'),
    path('o/authorize/', AuthorizationView.as_view(), name="authorize"),
    path('o/token/', TokenView.as_view(), name="token"),
    path('protected/', MyProtectedView.as_view()),
]


urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
