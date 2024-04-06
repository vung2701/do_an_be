from django.contrib import admin
from . import  models

admin.site.register(models.LanguageCode)
class LanguageCode(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id']
    list_filter = []
    inlines = []

admin.site.register(models.SrcCode)
class SrcCode(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name']
    list_display_links = ['id']
    list_filter = []
    inlines = []
