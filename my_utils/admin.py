from django.contrib import admin
from django.contrib.auth.models import Permission
from . import models


# Register your models here.


@admin.register(models.Template)
class TemplateAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['id', 'name', 'short_text', 'args', 'args_required']
    list_display_links = ['id']
    list_filter = []

    def short_text(self, obj):
        return f'{obj.text[:200] if obj.text else "n/a"}'


@admin.register(models.UploadFile)
class TemplateAdmin(admin.ModelAdmin):
    search_fields = ['name', 'file']
    list_display = ['id', 'name', 'owner', 'file', 'last_update']
    list_display_links = ['id']
    list_filter = []


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    search_fields = ['name', 'content_type__app_label', 'codename']
    list_display = ['id', 'name', 'content_type', 'codename', 'perm_name']
    list_display_links = ['id']
    list_filter = []

    def perm_name(self, obj):
        ct = obj.content_type.app_label
        name = obj.codename
        return "%s.%s" % (ct, name)
