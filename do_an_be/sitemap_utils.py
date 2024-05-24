from django.contrib.sitemaps import Sitemap
from django.conf import settings
from article.models import Article
from post.models import Post


class StaticViewSitemap(Sitemap):
    # protocol = 'http' if settings.DEBUG else 'https'
    protocol = 'http'
    static_url_list = [
        {'url': 'home', 'priority': 0.8, 'changefreq': "daily", 'location': '/'},
        {'url': 'articles', 'priority': 1.0, 'changefreq': "daily", 'location': '/articles'},
        # {'url': 'codes', 'priority': 0.8, 'changefreq': "weekly", 'location': '/code'},
        {'url': 'posts', 'priority': 0.8, 'changefreq': "daily", 'location': '/posts'}
    ]

    def items(self):
        return [item['url'] for item in self.static_url_list]

    def location(self, item):
        return {element['url']: element['location'] for element in self.static_url_list}[item]

    def priority(self, item):
        return {element['url']: element['priority'] for element in self.static_url_list}[item]

    def changefreq(self, item):
        return {element['url']: element['changefreq'] for element in self.static_url_list}[item]


class ArticlesViewSitemap(Sitemap):
    protocol = 'http'
    priority = 0.9

    def items(self):
        return Article.objects.filter().values('article_id', 'last_modified')

    def location(self, item):
        return f"/articles/{item.get('article_id')}"

    def lastmod(self, item):
        return item.get('last_modified')


class PostViewSitemap(Sitemap):
    protocol = 'http'
    priority = 0.5

    def items(self):
        return Post.objects.filter().values('post_id', 'last_modified')

    def location(self, item):
        return f"/posts/{item.get('post_id')}"

    def lastmod(self, item):
        return item.get('last_modified')
