# Generated by Django 4.2.7 on 2024-05-15 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_student_profile_student_user_student'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='student_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]