from django.contrib import admin
from .models import KnowledgeType, Knowledge

class KnowledgeTypeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['knowledge_type_id', 'name']
    list_display_links = ['knowledge_type_id']

class KnowledgeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['knowledge_id', 'name', 'get_knowledge_types']
    list_display_links = ['knowledge_id']
    list_filter = ['knowledge_types']


    def get_knowledge_types(self, obj):
        return ", ".join([kt.name for kt in obj.knowledge_types.all()])
    get_knowledge_types.short_description = 'Knowledge Types'

admin.site.register(KnowledgeType, KnowledgeTypeAdmin)
admin.site.register(Knowledge, KnowledgeAdmin)
