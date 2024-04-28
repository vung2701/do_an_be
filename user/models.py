import os
from PIL import Image
from django.contrib.sessions import base_session
from django.db import models
from django.contrib.auth.models import Group, User as AuthUser
from django.utils import timezone
from rest_framework.generics import ListAPIView
# from .serializer import ImageSerializer
from rest_framework import serializers
import uuid


class User(models.Model):
    base_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, null=True, default=None)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password1 = models.CharField(max_length=50)
    password2 = models.CharField(max_length=50)
    is_active = models.BooleanField(null=True)

    def __str__(self):
        return f'{self.first_name}-{self.last_name}'

    def to_dict(self):
        json_obj = dict(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            is_active=self.is_active,
            user_id=self.base_user.id if self.base_user else -1
        )
        return json_obj


class Profile(models.Model):
    user_id_profile = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField('user.User', on_delete=models.CASCADE)
    base_user = models.OneToOneField(to=AuthUser, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, null=True)
    image = models.ImageField(upload_to='user_profile', null=True, blank=True, default='user_profile/default.png')
    school = models.CharField(max_length=255, blank=True, null=True)
    major = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=1000, blank=True, null=True)
    phone = models.BigIntegerField(blank=True, null=True)
    DOB = models.DateField(blank=True, null=True)
    def __str__(self):
        return f'{self.user.__str__()} Profile'

    def save(self, *args, **kwargs):
        if not self.user_id_profile:
            self.user_id_profile = uuid.uuid4
        super().save(*args, **kwargs)
    


    def upload_to(instance, filename):
        return '/'.join(['images', str(instance.name), filename])

    def to_dict(self):
        return self.profile_to_dict()

    def profile_to_dict(self):
        profile = self
        return {
            'user_id': profile.user_id_profile,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'email': profile.email, 'image': profile.image.name, 'school': profile.school,
            'major': profile.major, 'location': profile.location,
            'phone': profile.phone,
            'DOB': profile.DOB,
        }


# class ProfileUser(User):
#     class Meta:
#         proxy = True


class UserImage(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    owner = models.ForeignKey(AuthUser, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    image = models.ImageField(upload_to='user_image', blank=True, null=True)

    last_update = models.DateTimeField(auto_now=True, db_index=True)
    create_time = models.DateTimeField(default=timezone.now, db_index=True)


class UserRole(object):
    user = 'role_user'
    ops = 'role Ops'
    admin = 'role_Admin'

    all = [user, ops, admin]


roles_group = [Group.objects.get_or_create(name=_)[0] for _ in UserRole.all]


class RoleModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(name__startswith='role_')


class Role(Group):
    objects = RoleModelManager()

    def role_name(self):
        return f'{self.name}'[5:] if self.name.startswith('role_') else 'N/A'

    class Meta:
        proxy = True






