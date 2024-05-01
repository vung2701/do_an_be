# Generated by Django 4.2.7 on 2024-05-01 07:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('src_code', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='srccode',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='src_code_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='srccode',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='srccode/'),
        ),
    ]