import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User as Auth_User
from user import models as user_models

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
    image = models.ImageField(upload_to='srccode/', null=True, blank=True)
    languages = models.ManyToManyField(LanguageCode, related_name='src_code_language', blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(Auth_User, on_delete=models.CASCADE, related_name='src_code_created_by', null=True,
                                   blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def to_dict(self):
        author_user_profile = user_models.Profile.objects.filter(base_user=self.created_by).first()
        author_user_id = author_user_profile.user_id_profile if author_user_profile else ''
        return {
            "src_code_id": self.src_code_id,
            "name": self.name,
            "content": self.content,
            "languages":  [language.name for language in self.languages.all()],
            "language_ids":[language.id for language in self.languages.all()],
            'created_by': author_user_id,
            'created_by_image': author_user_profile.image.name if author_user_profile else None,
        }
    