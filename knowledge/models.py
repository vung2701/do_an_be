import uuid
from django.db import models
from django.utils import timezone

from django.db import models
import uuid
from django.utils import timezone

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
    knowledge_types = models.ManyToManyField(KnowledgeType, related_name='knowledges')
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def to_dict(self):
        json_obj = dict(
            knowledge_id=self.knowledge_id,
            name=self.name,
            knowledge_types=[kt.name for kt in self.knowledge_types.all()]
        )
        return json_obj