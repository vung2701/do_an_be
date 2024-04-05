from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField


# Create your models here.
class Template(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    text = RichTextField(blank=True, null=True)
    args = models.CharField(max_length=255, default='', db_index=True, blank=True)
    args_required = models.CharField(max_length=255, default='', db_index=True, blank=True)

    last_update = models.DateTimeField(auto_now=True, db_index=True)
    create_time = models.DateTimeField(default=timezone.now, db_index=True)


class UploadFile(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, db_index=True)
    file = models.ImageField(upload_to='files', blank=True, null=True, db_index=True)

    last_update = models.DateTimeField(auto_now=True, db_index=True)
    create_time = models.DateTimeField(default=timezone.now, db_index=True)
