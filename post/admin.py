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
    search_fields = ['title',  'description' 'parent_post' ]
    list_display = [ 'title', 'description', 'parent_post', 'created_by']
    list_display_links = ['title']
    list_filter = []