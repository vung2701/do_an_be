from django.db import models
from django.contrib.auth.models import User as Auth_User
from django.utils import timezone
from django.core import serializers
from ckeditor.fields import RichTextField
import uuid
from knowledge.models import Knowledge
from src_code.models import SrcCode
from user import models as user_models


class Post(models.Model):
    post_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,db_index=True)
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='post/', null=True, blank=True)
    content = RichTextField(blank=True, null=True)
    src_code = models.ManyToManyField(SrcCode, related_name='post_src_code', blank=True)
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(Auth_User, on_delete=models.CASCADE, related_name='post_created_by', null=True,
                                   blank=True)
    last_modified = models.DateTimeField(default=timezone.now)
    likes = models.PositiveIntegerField(default=0)
    like_auth = models.ManyToManyField(to=Auth_User, related_name='post_auth_liker', blank=True)
    like_list = models.ManyToManyField(to=user_models.User, related_name='post_like_list', blank=True)
    comments = models.PositiveIntegerField(default=0)
    comment_list = models.ManyToManyField(to='post.CommentPost', related_name='post_comment_list', blank=True)
    comment_auth = models.ManyToManyField(to=Auth_User, related_name='post_auth_commenter', blank=True)
    STATUS_CHOICES = [('1', 'Open'), ('2', 'Closed')]
    status = models.CharField(choices=STATUS_CHOICES,
                              default='2', max_length=20)
    spotlight = models.BooleanField(default=False, db_index=True)
    spotlight_image = models.ImageField(upload_to='spotlight_image/', blank=True)
    spotlight_from = models.DateField(default=timezone.now, blank=True, null=True, db_index=True)
    spotlight_to = models.DateField(blank=True, null=True, db_index=True)
    def __str__(self):
        return self.title
    def to_dict(self):
        post = self
        author_user_profile = user_models.Profile.objects.filter(base_user=post.created_by).first()
        author_user_id = author_user_profile.user_id_profile if author_user_profile else ''

        return {
            'post_id': post.post_id,
            'title': post.title,
            'content': post.content,
            "created_on": post.created_on,
            'src_code': [src_code.src_code_id for src_code in post.src_code.all()],
            'likes': post.likes, 'like_list': [like.id for like in post.like_list.all()],
            'like_auth': [
                profile.user_id_profile
                for user in post.like_auth.all()
                for profile in user_models.Profile.objects.filter(base_user=user)
            ],
            'comments': post.comments,
            'comment_list': [comment.id for comment in post.comment_list.all()],
            'comment_auth': [comment.id for comment in post.comment_auth.all()],
            'created_by': author_user_id,
            'created_by_image': author_user_profile.image.name if author_user_profile else None,
            'created_by_name': author_user_profile.first_name + ' ' + author_user_profile.last_name ,
            'first_name_created_by': author_user_profile.first_name if author_user_profile else None,
            'last_name_created_by': author_user_profile.last_name if author_user_profile else None,
            'email_created_by': author_user_profile.email if author_user_profile else None,
            'school_created_by': author_user_profile.school if author_user_profile else None,
            'major_created_by': author_user_profile.major if author_user_profile else None,
            'spotlight': post.spotlight, 'spotlight_image': post.spotlight_image.name,
            'spotlight_from': post.spotlight_from, 'spotlight_to': post.spotlight_to,
        }

class CommentPost(models.Model):
    parent_post = models.ForeignKey(to=Post, on_delete=models.CASCADE, related_name='parent_post',
                                       blank=True, null=True,db_index=True)
    parent_comment = models.ForeignKey('post.CommentPost', default=None, blank=True,
                                       null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(Auth_User, on_delete=models.CASCADE, related_name='post_comment_creator', null=True)
    created_by_first_name = models.CharField(max_length=255, blank=True, null=True)
    created_by_last_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.description

    def to_dict(self):
        post_comment = self
        author_user_profile = user_models.Profile.objects.filter(base_user=post_comment.created_by).first()
        author_user_id = author_user_profile.user_id_profile if author_user_profile else ''

        return {
            'parent_post': post_comment.parent_post.post_id,
            'parent_comment': post_comment.parent_comment,
            'title': post_comment.title,
            "description": post_comment.description,
            'created_on': post_comment.created_on,
        }