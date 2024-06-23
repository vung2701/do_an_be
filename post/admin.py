from django.contrib import admin
from .models import Post,CommentPost
# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ['title']
    list_display = ['title', 'created_by','post_id', 'status']
    list_display_links = ['title']
    list_filter = ['status']
    list_per_page = 10 

@admin.register(CommentPost)
class CommentPostAdmin(admin.ModelAdmin):
    search_fields = [ 'description' 'parent_post' ]
    list_display = [ 'id', 'description', 'parent_post', 'created_by', 'created_on']
    list_filter = []
    list_per_page = 10 
