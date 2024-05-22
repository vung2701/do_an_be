import json
from django.db import models
from django.contrib.auth.models import User as Auth_User
from django.utils import timezone
from django.core import serializers
from ckeditor.fields import RichTextField
import uuid
from knowledge.models import Knowledge
from src_code.models import SrcCode
from user import models as user_models

class Article(models.Model):
    article_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,db_index=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True, null=True)
    author_user = models.ForeignKey(to=user_models.User, related_name='author_user', on_delete=models.CASCADE,
                                    blank=True, null=True)
    author_description = models.TextField(default='Please do not leave me blank')
    published_on = models.DateField()
    image = models.ImageField(upload_to='article/')
    content = RichTextField(blank=True, null=True)
    knowledge = models.ManyToManyField(Knowledge, related_name='article_knowledge', blank=True)
    src_code = models.ManyToManyField(SrcCode, related_name='article_src_code', blank=True)
    spotlight = models.BooleanField(default=None, db_index=True)
    spotlight_image = models.ImageField(upload_to='spotlight_image/', blank=True)
    spotlight_from = models.DateField(default=timezone.now, blank=True, null=True, db_index=True)
    spotlight_to = models.DateField(blank=True, null=True, db_index=True)
    likes = models.PositiveIntegerField(default=0)
    like_list = models.ManyToManyField(to=Auth_User, related_name='article_like_list', blank=True)
    like_auth = models.ManyToManyField(to=Auth_User, related_name='article_auth_liker', blank=True)
    comments = models.PositiveIntegerField(default=0)
    comment_list = models.ManyToManyField(to='article.Comment', related_name='article_comment_list', blank=True)
    comment_auth = models.ManyToManyField(to=Auth_User, related_name='article_auth_commenter', blank=True)
    reference_link = models.URLField(max_length=255, blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(Auth_User, on_delete=models.CASCADE, related_name='article_created_by', null=True,
                                   blank=True)
    last_modified = models.DateTimeField(default=timezone.now)

    @property
    def get_spotlight_image_url(self):
        if self.spotlight_image and hasattr(self.spotlight_image, 'url'):
            return self.spotlight_image.url
        else:
            return "/0.jpg"

    def save(self, *args, **kwargs):
        if not self.article_id:
            self.article_id = uuid.uuid4()
        super().save(*args, **kwargs)

    def to_dict(self):
        return self.article_to_dict(get_full=False)

    def article_to_dict(self, get_full=True):
        article = self
        author_user_profile = user_models.Profile.objects.filter(base_user=article.author_user.base_user).first()
        author_user_id = author_user_profile.user_id_profile if author_user_profile else ''

        return {
            'article_id': article.article_id,
            'title': article.title,
            'author': article.author,
            'author_user_id': author_user_id,
            'author_img': author_user_profile.image.name,
            'author_username': author_user_profile.first_name + ' ' + author_user_profile.last_name,
            'author_major': author_user_profile.major,
            'author_school': author_user_profile.school,
            'author_description': article.author_description,
            'published_on': article.published_on,
            'image': article.image.name,
            'content': article.content if get_full else article.content[:2000],
            'src_code': [src_code.src_code_id for src_code in article.src_code.all()],
            'knowledge': [knowledge.knowledge_id for knowledge in article.knowledge.all()],
            'reference_link': article.reference_link,
            'spotlight': article.spotlight, 'spotlight_image': article.spotlight_image.name,
            'spotlight_from': article.spotlight_from, 'spotlight_to': article.spotlight_to,
            "created_on": article.created_on, 'created_by': article.created_by.id if article.created_by else None,
            'likes': article.likes, 'like_list': [like.id for like in article.like_list.all()],
            'like_auth': [
                profile.user_id_profile
                for user in article.like_auth.all()
                for profile in user_models.Profile.objects.filter(base_user=user)
            ],
            'comments': article.comments,
            'comment_list': [comment.id for comment in article.comment_list.all()],
            'comment_auth': [comment.id for comment in article.comment_auth.all()],
            'limit': False if get_full else True,
        }

    def article_short(self):
        article = self

        return {
            'article_id': article.article_id,
            'title': article.title,
            'author_user': article.author_user,
            'published_on': article.published_on,
            'image': article.image.name,
            'content': article.content[:1000],
        }

    def __str__(self):
        return f'{self.title}-{self.author_user}-{self.published_on}'

class Comment(models.Model):
    parent_article = models.ForeignKey(to=Article, on_delete=models.CASCADE, related_name='parent_article',
                                       blank=True, null=True)
    parent_comment = models.ForeignKey('article.Comment', default=None, blank=True,
                                       null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    attachment = models.FileField(upload_to='comment_article/', blank=True, null=True)
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(user_models.User, on_delete=models.CASCADE, related_name='comment_creator', null=True)
    created_by_first_name = models.CharField(max_length=255, blank=True, null=True)
    created_by_last_name = models.CharField(max_length=255, blank=True, null=True)
    created_by_image = models.ImageField(upload_to='user_image', null=True, blank=True)
    last_modified = models.DateTimeField(default=timezone.now)
    likes = models.PositiveIntegerField(default=0)
    like_list = models.ManyToManyField(to=user_models.User, related_name='comment_like_list', blank=True)
    like_auth = models.ManyToManyField(to=Auth_User, related_name='comment_auth_liker', blank=True)
    comments = models.PositiveIntegerField(default=0)
    comment_list = models.ManyToManyField(to='article.Comment', related_name='comment_comment_list', blank=True)
    comment_auth = models.ManyToManyField(to=Auth_User, related_name='comment_auth_commenter', blank=True)

    def to_dict(self):
        json_obj = json.loads(serializers.serialize('json', [self]))[0].get('fields')
        json_obj['id'] = self.id
        json_obj[
            'created_by_user'] = self.created_by.base_user.username if self.created_by and self.created_by.base_user else 'anonymous'
        comment = self
        try:
            return {
                'parent_article': comment.parent_article.article_id,
                'parent_comment': comment.parent_comment.id if comment.parent_comment else None,
                'title': comment.title,
                'description': comment.description,
                'attachment': comment.attachment.name,
                'created_on': comment.created_on,
                'created_by': comment.created_by.id,
                'created_by_first_name': comment.created_by_first_name,
                'created_by_last_name': comment.created_by_last_name,
                'created_by_image': comment.created_by_image.name,
                'last_modified': comment.last_modified,
                'likes': comment.likes,
                'like_list': [user.id for user in comment.like_list.all()],
                'like_auth': [user.id for user in comment.like_auth.all()],
                'comments': comment.comments,
                'comment_auth': [user.id for user in comment.comment_auth.all()],
                'comment_list': [comment.id for comment in comment.comment_list.all()],
            }
        except Exception as e:
            # Print or log the error for debugging purposes
            print(f"Error in comment_to_dict(): {e}")
            return {'error': 'Failed to convert comment to dictionary'}

    def comment_to_dict(self):
        comment = self
        try:
            return {
                'parent_article': comment.parent_article.article_id,
                'parent_comment': comment.parent_comment.id if comment.parent_comment else None,
                'title': comment.title,
                'description': comment.description,
                'attachment': comment.attachment.name,
                'created_on': comment.created_on,
                'created_by': comment.created_by.id,
                'created_by_first_name': comment.created_by_first_name,
                'created_by_last_name': comment.created_by_last_name,
                'created_by_image': comment.created_by_image.name,
                'last_modified': comment.last_modified,
                'likes': comment.likes,
                'like_list': [user.id for user in comment.like_list.all()],
                'comments': comment.comments,
                'comment_auth': [user.id for user in comment.comment_auth.all()],
                'comment_list': [comment.id for comment in comment.comment_list.all()],
            }
        except Exception as e:
            # Print or log the error for debugging purposes
            print(f"Error in comment_to_dict(): {e}")
            return {'error': 'Failed to convert comment to dictionary'}

    def __str__(self):
        return f'{self.title}-{self.created_by}-{self.last_modified}'