from django.contrib import admin
from .models import Post,CommentPost
# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['title', 'created_by','post_id','spotlight', 'status']
    list_display_links = ['title']
    list_filter = []
@admin.register(CommentPost)
class CommentPostAdmin(admin.ModelAdmin):
    search_fields = ['parent_post', 'title', 'description']
    list_display = ['parent_post', 'title', 'description', 'created_by', 'last_modified']
    list_display_links = ['title']
    list_filter = []