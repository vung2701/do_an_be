# Generated by Django 4.2.7 on 2024-04-04 11:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('knowledge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='knowledge',
            name='created_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='knowledge',
            name='modified_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
