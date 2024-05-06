from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from my_utils.authentication import SessionAuthentication, TokenAuthentication
from my_utils import utils
from my_utils.schema import schema
import logging
import hashlib
from .models import Post, CommentPost
from user.models import Profile, User
from django.contrib.auth.models import User as Auth_User
from django.utils import timezone
from datetime import datetime
import ast
import os

# Create your views here.
get_post_schemas = {
    'properties': {'title': 'title', 'image': 'image', 'content': 'content', 'created_on': 'created_on',
                   'created_by': 'created_by', 'likes': 'likes', 'like_auth': 'like_auth', 'comments': 'comments',
                   'comment_list': 'comment_list', 'comment_auth': 'comment_auth', 'post_id': 'post_id', 'id': 'id'},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
@schema(schema=get_post_schemas)
def create_post(request, params):
    if request.method == 'POST':
        user_profile = Profile.objects.filter(user_id_profile=params.get('created_by')).first()
        post, created = Post.objects.get_or_create(id=params.get('id'))
        if created:
            post.created_on = timezone.now()
            post.created_by = user_profile.base_user
        post.title = params.get('title')
        post.content = params.get('content')
        post.modified_on = timezone.now()
        post.save()
        ret = dict(error=0, post=utils.obj_to_dict(post))
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes(( TokenAuthentication,))
@schema(schema=get_post_schemas)
def update(request, params):
    if request.method == 'POST':
        post = Post.objects.filter(post_id=params.get('post_id')).first()
        if (request.user) != post.created_by:
            ret = dict(error=1, message='You do not have permission to edit this post')
            return JsonResponse(status=403, data=ret)
        if params.get('title'):
            post.title = params.get('title')
        if params.get('content'):
            post.content = params.get('content')
        post.modified_on = timezone.now()
        post.save()
        ret = dict(error=0, post=utils.obj_to_dict(post))
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
@schema(schema=get_post_schemas)
def get_post(request, params):
    if request.method == 'GET':
        if params.get('post_id') is not None:
            post = Post.objects.filter(post_id=params.get('post_id')).first()
            ret = dict(error=0, post=utils.obj_to_dict(post))
        else:
            payload = utils.get_payload(request.GET, get_post_schemas['properties'])
            posts = Post.objects.filter(status='1') 
            ret = utils.get_data_in_page_and_fields(posts, 'post', payload, request.GET)
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
@schema(schema=get_post_schemas)
def post_like(request, params):
    if request.method == 'POST':
        post = Post.objects.filter(post_id=params.get('post_id')).first()
        if post:
            if params.get('#') != '':
                post.likes += 1
                auth_user_profile = Profile.objects.filter(user_id_profile=params.get('like_auth')).first()
                auth_user_id = auth_user_profile.base_user_id
                base_user = Auth_User.objects.filter(id=auth_user_id).first()
                liker = User.objects.filter(base_user=base_user).first()
                post.like_list.add(liker)
                post.like_auth.add(base_user)
                post.save()
            ret = dict(error=0, article=utils.obj_to_dict(post))
            return JsonResponse(data=ret)
        else:
            ret = dict(error=1, message='Post not found')
            return JsonResponse(status=400, data=ret)
    else:
        return HttpResponse(status=403)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
@schema(schema=get_post_schemas)
def post_unlike(request, params):
    if request.method == 'POST':
        post = Post.objects.filter(post_id=params.get('post_id')).first()
        if params.get('like_auth') != '':
            post.likes -= 1
            auth_user_profile = Profile.objects.filter(user_id_profile=params.get('like_auth')).first()
            auth_user_id = auth_user_profile.base_user_id
            base_user = Auth_User.objects.filter(id=auth_user_id).first()
            liker = User.objects.filter(base_user=base_user).first()
            post.like_list.remove(liker)
            post.like_auth.remove(base_user)
            post.save()
            ret = dict(error=0, article=utils.obj_to_dict(post))
            return JsonResponse(data=ret)
        else:
            ret = dict(error=1, message='No post found')
            return JsonResponse(status=400, data=ret)
    else:
        return HttpResponse(status=403)


get_comment_schemas = {
    'properties': {'title': 'title', 'description': 'description', 'parent_post': 'parent_post_id',
                   'parent_comment': 'parent_comment__id', 'created_by': 'created_by',
                   'created_by_first_name': 'created_by_first_name',
                   'created_by_last_name': 'created_by_last_name',
                   'created_by_image': 'created_by_image',
                   'comment_id': 'comment_id', 'like_list': 'like_list',
                   'like_auth': 'like_auth'},
    'required': [],
    'bool_args': [],
    'int_args': ['parent_comment__id'],
    'float_args': [],
}


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@schema(schema=get_comment_schemas)
def post_comment(request, params):
    if request.method == 'POST':
        post = Post.objects.filter(post_id=params.get('parent_post_id')).first()
        base_user = Auth_User.objects.filter(id=request.user.id).first()

        comment = CommentPost.objects.create(
            title=params.get('title'),
            parent_post=post,
            description=params.get('description'),
            created_by=base_user
        )
        comment.created_by_first_name = comment.created_by.first_name
        comment.created_by_last_name = comment.created_by.last_name
        profile = Profile.objects.filter(base_user=comment.created_by).first()
        comment.created_by_image = profile.image
        comment.save()
        post.comments += 1
        post.save()
        ret = dict(error=0, comment=utils.obj_to_dict(comment))
        return JsonResponse(data=ret)
    elif request.method == 'GET':
        if params.get('parent_post_id'):
            post = Post.objects.filter(post_id=params.get('parent_post_id')).first()
            id = post.id
            comments = CommentPost.objects.filter(parent_post=post)
            article_id_value = request.GET.get('article_id')
            request.GET = request.GET.copy()
            request.GET['parent_post'] = id
            payload = utils.get_payload(request.GET, get_comment_schemas['properties'])
            ret = utils.get_data_in_page_and_fields(comments, 'comment', payload, request.GET)
            return JsonResponse(ret)
        else:
            comments = CommentPost.objects.all()
            comment_list = [comment.to_dict() for comment in comments]
            ret = dict(error=0, comment=utils.obj_to_dict(comment_list))
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)
    