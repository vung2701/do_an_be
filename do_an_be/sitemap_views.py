from django.views.decorators.cache import cache_page
from django.contrib.sitemaps import Sitemap
from django.shortcuts import render
from django.conf import settings
from datetime import datetime

from .sitemap_utils import StaticViewSitemap, ArticlesViewSitemap, PostViewSitemap

sitemaps = {
    "page": StaticViewSitemap,
    "articles": ArticlesViewSitemap,
    "posts": PostViewSitemap,
}


@cache_page(60 * 60)
def page_robots(request):
    context = dict(sitemaps=sitemaps, today=datetime.utcnow().isoformat(),
                   site_addr=f'{request.scheme}://{request.get_host()}')
    return render(request, "robots.txt", context=context, content_type='text/plain')


@cache_page(60 * 60)
def sitemapindex(request):
    context = dict(sitemaps=sitemaps, today=datetime.utcnow().isoformat(),
                   site_addr=f'{request.scheme}://{request.get_host()}')
    return render(request, "sitemapindex.xml", context=context, content_type='text/xml')
