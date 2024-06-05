from import_export import resources, fields
import os
from django.db import models
from django.contrib.auth.models import Group, User as AuthUser
from django.utils import timezone
# from .serializer import ImageSerializer
from import_export.widgets import ForeignKeyWidget
import uuid
class Student(models.Model):
    student_id = models.CharField(max_length=255,  null=False, unique=True)
    student_class = models.CharField(max_length=255, blank=True, null=True)
    is_use=models.BooleanField(default=False)
    def __str__(self):
        return self.student_id

    def to_dict(self):
        json_obj = dict(
            id=self.id,
            student_id=self.student_id,
            student_class=self.student_class,
            is_use=self.is_use
        )
        return json_obj


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('student_id', 'student_class')
        import_id_fields = ('student_id',)

class User(models.Model):
    base_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, null=True, default=None)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password1 = models.CharField(max_length=50)
    password2 = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    student = models.OneToOneField(Student, on_delete=models.SET_NULL, null=True, blank=True) 

    def __str__(self):
        return f'{self.first_name}-{self.last_name}'
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update the student field in the associated Profile model if it exists
        if self.profile and self.profile.student != self.student:
            self.profile.student = self.student
            self.profile.save()

    def to_dict(self):
        json_obj = dict(
            id=self.id,
            student_id=self.student.student_id if self.student else None,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            is_active=self.is_active,
            user_id=self.base_user.id if self.base_user else -1
        )
        return json_obj


class Profile(models.Model):
    user_id_profile = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    modified_on = models.DateTimeField(default=timezone.now)
    created_on = models.DateTimeField(default=timezone.now)
    student = models.OneToOneField(Student, on_delete=models.SET_NULL, null=True, blank=True) 
    def __str__(self):
        return f'{self.user.__str__()} Profile'

    def save(self, *args, **kwargs):
        if not self.user_id_profile:
            self.user_id_profile = uuid.uuid4
        super().save(*args, **kwargs)
        if self.user and self.user.student != self.student:
            self.user.student = self.student
            self.user.save()
            
        if self.student:
            self.student.is_use = True
            self.student.save()
    
    def delete(self, *args, **kwargs):
        if self.student:
            self.student.is_use = False
            self.student.save()
        super().delete(*args, **kwargs)
    
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
            'student_id': self.student.student_id if self.student else None,
            'class': self.student.student_class if self.student else None
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






