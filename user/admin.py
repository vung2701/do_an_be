from django import forms
from django.urls import path
from django.contrib import admin
from django.shortcuts import redirect, render
from django.utils.html import format_html
import pandas as pd
from .models import Profile, StudentResource, User
from . import models
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Student
class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    search_fields = ['student_id']
    list_display = ('id', 'student_id', 'student_class', 'is_use')
    list_filter = ['student_class', 'is_use']

admin.site.register(Student, StudentAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user_id_profile', 'base_user__username', 'base_user__email', 'base_user__first_name',
                     'base_user__last_name']
    list_display = ['id', 'user', 'image', 'base_user', 'user_id_profile']
    list_display_links = ['id']
    list_filter = []
    inlines = []


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = [ 'base_user__username', 'base_user__email', 'base_user__first_name',
                     'base_user__last_name']
    list_display = ('id', 'student', 'is_active')
    list_display_links = ['id']
    list_filter = []

    inlines = []

    def user_profile(self, obj):
        new_profile, created = Profile.objects.get_or_create(user=obj)
        obj.profile = new_profile
        obj.save()
        return f'{obj.profile}'

    def user_id(self, obj):
        return f'{obj.base_user.id}' if obj.base_user else ''


@admin.register(models.UserImage)
class UserImageAdmin(admin.ModelAdmin):
    search_fields = []
    list_display = ['id', 'name', 'owner', 'image']
    list_display_links = ['id']
    list_filter = []
    inlines = []
    ordering = ['-last_update']


# admin.site.register(UploadImageTest)


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    search_fields = ['name', 'user__email', 'user__username', 'user__first_name']
    list_display = ['id', 'role_name', 'users']
    list_display_links = ['id']
    list_filter = []
    inlines = []
    ordering = []

    def users(self, obj):
        return format_html('<br>'.join(obj.user_set.filter().values_list('username', flat=True)))

# admin.site.register(UploadImageTest)

