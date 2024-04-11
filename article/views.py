from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from my_utils.authentication import SessionAuthentication, TokenAuthentication
from my_utils import utils
from my_utils.schema import schema
from .models import  Article, Comment
from user.models import User, Profile
from django.contrib.auth.models import User as Auth_User
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils import timezone
from datetime import datetime
import ast
import requests
from bs4 import BeautifulSoup
import os
import uuid
from . import filter_articles
from django.conf import settings

get_article_schemas = {
    'properties': {'title': 'title','article_id': 'article_id','published_on': 'published_on',
                   'knowledge': 'knowledge','src_code': 'src_code', 'like_auth': 'like_auth', 'like_list': 'like_list',
                    'spotlight_from': 'spotlight_from',
                   'spotlight_to': 'spotlight_to', 'likes': 'likes', 'published_from': 'published_from',
                  'author_id': 'author_user',
                   },
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
# @avt_permission_required(perm=['news.view_article'])
@schema(schema=get_article_schemas)
def get_article(request, params):
    """
    Get office IPs
    :param request:
    :param params:
    :return:
    """
    published_from = params.get('published_from')
    published_to = params.get('published_to')
    author_user = params.get('author_user')
    if request.method == 'GET':
        if published_from is not None or published_to is not None or author_user is not None:
            payload = utils.get_payload(request.GET, get_article_schemas['properties'])
            filter = filter_articles.filter_article(payload,published_from,published_to,author_user)
            ret = utils.get_data_in_page_and_fields(Article, 'article', filter, request.GET, )
        else:
            payload = utils.get_payload(request.GET, get_article_schemas['properties'])
            ret = utils.get_data_in_page_and_fields(Article, 'article', payload, request.GET, )
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)
    

    
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
# @avt_permission_required(perm=['news.view_article'])
@schema(schema=get_article_schemas)
def article_like(request, params):
    if request.method == 'POST':
        article = Article.objects.filter(article_id=params.get('article_id')).first()
        if article:
            if params.get('like_auth') != '':
                article.likes += 1
                auth_user_profile = Profile.objects.filter(user_id_profile=params.get('like_auth')).first()
                auth_user_id = auth_user_profile.base_user_id
                base_user = Auth_User.objects.filter(id=auth_user_id).first()
                liker = User.objects.filter(base_user=base_user).first()
                article.like_list.add(liker)
                article.like_auth.add(base_user)
                article.save()
            ret = dict(error=0, article=utils.obj_to_dict(article))
            return JsonResponse(data=ret)
        else:
            ret = dict(error=1, message='Article not found')
            return JsonResponse(status=400, data=ret)
    else:
        return HttpResponse(status=403)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
# @avt_permission_required(perm=['news.change_article'])
@schema(schema=get_article_schemas)
def article_unlike(request, params):
    if request.method == 'POST':
        article = Article.objects.filter(article_id=params.get('article_id')).first()
        if params.get('like_auth') != '':
            article.likes -= 1
            auth_user_profile = Profile.objects.filter(user_id_profile=params.get('like_auth')).first()
            auth_user_id = auth_user_profile.base_user_id
            base_user = Auth_User.objects.filter(id=auth_user_id).first()
            liker = User.objects.filter(base_user=base_user).first()
            article.like_list.remove(liker)
            article.like_auth.remove(base_user)
            article.save()
            ret = dict(error=0, article=utils.obj_to_dict(article))
            return JsonResponse(data=ret)
        else:
            ret = dict(error=1, message='No article found')
            return JsonResponse(status=400, data=ret)
    else:
        return HttpResponse(status=403)
    
    
get_comment_schemas = {
    'properties': {'title': 'title', 'description': 'description', 'parent_article': 'parent_article_id',
                   'parent_comment': 'parent_comment__id', 'attachment': 'attachment', 'created_by': 'created_by',
                   'created_by_first_name': 'created_by_first_name',
                   'created_by_last_name': 'created_by_last_name',
                   'created_by_image': 'created_by_image',
                   'comment_id': 'comment_id', 'like_list': 'like_list', 'share_list': 'share_list',
                   'like_auth': 'like_auth', 'share_auth': 'share_auth', },
    'required': [],
    'bool_args': [],
    'int_args': ['parent_comment__id'],
    'float_args': [],
}

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@schema(schema=get_comment_schemas)
def article_comment(request, params):
    if request.method == 'POST':
        base_user = Auth_User.objects.filter(id=request.user.id).first()
        user = User.objects.filter(base_user=base_user).first()
        comment = Comment.objects.create(
            title=params.get('title'),
            parent_article=Article.objects.filter(article_id=params.get('parent_article_id')).first(),
            description=params.get('description'),
            attachment=params.get('attachment'),
            created_by = user
        )
        comment.created_by_first_name = comment.created_by.first_name
        comment.created_by_last_name = comment.created_by.last_name
        comment.save()
        profile = Profile.objects.filter(user=comment.created_by).first()
        comment.created_by_image = profile.image
        if params.get('parent_comment__id') is not None:
            parent_comment = Comment.objects.filter(id=int(params.get('parent_comment__id'))).first()
            comment.parent_comment = parent_comment
            comment.parent_article = parent_comment.parent_article
        comment.save()
        ret = dict(error=0, comment=utils.obj_to_dict(comment))
        return JsonResponse(data=ret)
    elif request.method == 'GET':
        if params.get('parent_article_id'):
            article = Article.objects.filter(article_id=params.get('parent_article_id')).first()
            id = article.id
            comments = Comment.objects.filter(parent_article=article)
            article_id_value = request.GET.get('article_id')
            request.GET = request.GET.copy()
            request.GET['parent_article'] = id
            payload = utils.get_payload(request.GET, get_comment_schemas['properties'])
            ret = utils.get_data_in_page_and_fields(comments, 'comment', payload, request.GET)
            return JsonResponse(ret)
        else:
            comments = Comment.objects.all()
            comment_list = [comment.to_dict() for comment in comments]
            ret = dict(error=0, comment=utils.obj_to_dict(comment_list))
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)

