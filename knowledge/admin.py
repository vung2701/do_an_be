from django.contrib import admin

from django.contrib import admin
from . import  models

admin.site.register(models.KnowledgeType)
class KnowledgeType(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name']
    list_display_links = ['id']
    list_filter = []
    inlines = []

admin.site.register(models.Knowledge)
class Knowledge(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name']
    list_display_links = ['id']
    list_filter = []
    inlines = []