from django.contrib import admin
from django.contrib import admin

from django.contrib import admin
from . import  models

@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    search_fields = ['title', 'author', 'content']
    list_display = ['title', 'author', 'published_on', 'reference_link', 'last_modified']
    list_display_links = ['title']
    list_filter = []

admin.site.register(models.Comment)
class Comment(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['id', 'title', 'description','create_on', 'create_by']
    list_display_links = ['id']
    list_filter = []
    inlines = []