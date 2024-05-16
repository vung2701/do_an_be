from django.db.models.signals import post_save, pre_save 
from django.dispatch import receiver
from .models import Student


@receiver(post_save, sender=Student)
def check_and_delete_empty_student(sender, instance, **kwargs):
    if instance.student_id == '':
        instance.delete()