# Generated by Django 4.2.7 on 2024-04-12 14:25

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CommentPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by_first_name', models.CharField(blank=True, max_length=255, null=True)),
                ('created_by_last_name', models.CharField(blank=True, max_length=255, null=True)),
                ('last_modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('likes', models.PositiveIntegerField(default=0)),
                ('comments', models.PositiveIntegerField(default=0)),
                ('comment_auth', models.ManyToManyField(blank=True, related_name='post_comment_auth_commenter', to=settings.AUTH_USER_MODEL)),
                ('comment_list', models.ManyToManyField(blank=True, related_name='post_comment_comment_list', to='post.commentpost')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_comment_creator', to=settings.AUTH_USER_MODEL)),
                ('like_auth', models.ManyToManyField(blank=True, related_name='post_comment_auth_liker', to=settings.AUTH_USER_MODEL)),
                ('parent_comment', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='post.commentpost')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post_id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('image', models.ImageField(blank=True, null=True, upload_to='post/')),
                ('content', ckeditor.fields.RichTextField(blank=True, null=True)),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('likes', models.PositiveIntegerField(default=0)),
                ('comments', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('1', 'Open'), ('2', 'Closed')], default='1', max_length=20)),
                ('spotlight', models.BooleanField(db_index=True, default=False)),
                ('spotlight_image', models.ImageField(blank=True, upload_to='spotlight_image/')),
                ('spotlight_from', models.DateField(blank=True, db_index=True, default=django.utils.timezone.now, null=True)),
                ('spotlight_to', models.DateField(blank=True, db_index=True, null=True)),
                ('comment_auth', models.ManyToManyField(blank=True, related_name='post_auth_commenter', to=settings.AUTH_USER_MODEL)),
                ('comment_list', models.ManyToManyField(blank=True, related_name='post_comment_list', to='post.commentpost')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_created_by', to=settings.AUTH_USER_MODEL)),
                ('like_auth', models.ManyToManyField(blank=True, related_name='post_auth_liker', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='commentpost',
            name='parent_post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent_post', to='post.post'),
        ),
    ]