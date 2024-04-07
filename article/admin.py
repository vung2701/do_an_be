from django.contrib import admin
from django.contrib import admin

from django.contrib import admin
from . import  models

admin.site.register(models.Article)
class Article(admin.ModelAdmin):
    search_fields = ['title', 'author_user']
    list_display = ['id','article_id', 'title', 'author_user', 'published_on', 'create_on', 'create_by']
    list_display_links = ['id']
    list_filter = []
    inlines = []

admin.site.register(models.Comment)
class Comment(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['id', 'title', 'description','create_on', 'create_by']
    list_display_links = ['id']
    list_filter = []
    inlines = []