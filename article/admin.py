from django.contrib import admin
from django.contrib import admin

from django.contrib import admin
from . import  models

@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    search_fields = ['title', 'author', 'content']
    list_display = ['title', 'author', 'published_on']
    list_display_links = ['title']
    list_filter = []

@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = ['description' 'parent_article' ]
    list_display = [ 'id', 'description', 'parent_article', 'created_by', 'created_on']
    list_filter = []