from django.contrib import admin
from . import models
# Register your models here.
@admin.register(models.Device)
class DeviceAdmin(admin.ModelAdmin):
    search_fields = []
    list_display = ['id', 'custom_fingerprint']
    list_display_links = ['id']
    list_filter = []
    inlines = []
    ordering = []

@admin.register(models.WebBrowser)
class WebBrowserAdmin(admin.ModelAdmin):
    search_fields = []
    list_display = ['id', 'custom_fingerprint']
    list_display_links = ['id']
    list_filter = []
    inlines = []
    ordering = []

@admin.register(models.IPObject)
class IPObjectAdmin(admin.ModelAdmin):
    search_fields = []
    list_display = ['id', 'ip_address']
    list_display_links = ['id']
    list_filter = []
    inlines = []
    ordering = []

@admin.register(models.PublicUser)
class PublicUserAdmin(admin.ModelAdmin):
    search_fields = []
    list_display = ['id','web_browser']
    list_display_links = ['id']
    list_filter = []
    inlines = []
    ordering = []

@admin.register(models.ReadingList)
class ReadingListAdmin(admin.ModelAdmin):
    search_fields = []
    list_display = ['id','public_user', 'remain','current_month_access']
    list_display_links = ['id']
    list_filter = []
    inlines = []
    ordering = []