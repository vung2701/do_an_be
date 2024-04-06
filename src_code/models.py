import uuid
from django.db import models
from django.utils import timezone

# Create your models here.
class LanguageCode(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }
    
class SrcCode(models.Model):
    src_code_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    content = models.TextField()
    languages = models.ManyToManyField(LanguageCode, related_name='src_code_language', blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def to_dict(self):
        language_names = [language.name for language in self.languages.all()]
        return {
            "src_code_id": self.src_code_id,
            "name": self.name,
            "content": self.content,
            "languages": language_names,
        }
    