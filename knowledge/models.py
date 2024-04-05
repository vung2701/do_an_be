import uuid
from django.db import models
from django.utils import timezone

# Create your models here.
class KnowledgeType(models.Model):
    knowledge_type_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
    def to_dict(self):
        json_obj = dict(
            knowledge_type_id=self.knowledge_type_id,
            name=self.name,
        )
        return json_obj
    
class Knowledge(models.Model):
    knowledge_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    knowledge_type = models.ForeignKey(KnowledgeType, on_delete=models.CASCADE)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def to_dict(self):
        json_obj = dict(
            knowledge_id=self.knowledge_id,
            name=self.name,
            knowledge_type = self.knowledge_type.name
        )
        return json_obj