import uuid
from django.db import models
from django.utils import timezone

# Create your models here.
class LangugeCode(models.Model):
    language_code_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
    def to_dict(self):
        json_obj = dict(
            language_code_id=self.language_code_id,
            name=self.name,
        )
        return json_obj
    
class SrcCode(models.Model):
    src_code_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    content = models.TextField()
    language = models.ManyToManyField(LangugeCode, related_name='laguages', blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def to_dict(self):
        json_obj = dict(
            src_code_id=self.knowledge_id,
            name=self.name,
            language_code = self.language
        )
        return json_obj