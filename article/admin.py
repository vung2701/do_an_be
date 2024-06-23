from django.contrib import admin
from .models import Article, Comment
from knowledge.models import Knowledge, KnowledgeType
from django.utils.translation import gettext_lazy as _

class KnowledgeTypeFilter(admin.SimpleListFilter):
    title = _('knowledge type')
    parameter_name = 'knowledge_type'

    def lookups(self, request, model_admin):
        knowledge_types = set(KnowledgeType.objects.all())
        return [(kt.id, kt.name) for kt in knowledge_types]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(knowledge__knowledge_types__id=self.value()).distinct()
        return queryset

class ArticleAdmin(admin.ModelAdmin):
    search_fields = ['title', 'author', 'content']
    list_display = ['title', 'author', 'get_knowledges', 'get_knowledge_types', 'published_on']
    list_display_links = ['title']
    list_filter = [KnowledgeTypeFilter]
    list_per_page = 10 

    def get_knowledges(self, obj):
        return ", ".join([knowledge.name for knowledge in obj.knowledge.all()])
    get_knowledges.short_description = 'Knowledges'

    def get_knowledge_types(self, obj):
        knowledge_types = set()
        for knowledge in obj.knowledge.all():
            for knowledge_type in knowledge.knowledge_types.all():
                knowledge_types.add(knowledge_type.name)
        return ", ".join(knowledge_types)
    get_knowledge_types.short_description = 'Knowledge Types'

class CommentAdmin(admin.ModelAdmin):
    search_fields = ['description', 'parent_article']
    list_display = ['id', 'description', 'parent_article', 'created_by', 'created_on']
    list_filter = []
    list_per_page = 10 

admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment, CommentAdmin)
