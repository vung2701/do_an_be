from django.contrib import admin
from .models import SrcCode, LanguageCode

class LanguageCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['id']

class SrcCodeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['src_code_id', 'name', 'get_languages']
    list_display_links = ['src_code_id']
    list_filter = ['languages']

    def get_languages(self, obj):
        return ", ".join([lang.name for lang in obj.languages.all()])
    get_languages.short_description = 'Languages'

admin.site.register(LanguageCode, LanguageCodeAdmin)
admin.site.register(SrcCode, SrcCodeAdmin)