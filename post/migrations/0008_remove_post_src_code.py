# Generated by Django 4.2.7 on 2024-06-05 02:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0007_remove_commentpost_comment_auth_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='src_code',
        ),
    ]
