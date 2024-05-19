from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from knowledge.models import Knowledge, KnowledgeType
from my_utils.authentication import SessionAuthentication, TokenAuthentication
from my_utils import utils
from my_utils.schema import schema
from post.models import Post
from unreg_user.models import Device, IPObject, PublicUser, ReadingList, WebBrowser
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
            created_by = user
        )
        comment.created_by_first_name = comment.created_by.first_name
        comment.created_by_last_name = comment.created_by.last_name
        comment.save()
        profile = Profile.objects.filter(user=comment.created_by).first()
        comment.created_by_image = profile.image
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


get_spotlight_schemas = {
    'properties': {'category': 'category', 'item_id': 'item_id', 'spotlight_image': 'spotlight_image',
                   'spotlight_from': 'spotlight_from', 'spotlight_to': 'spotlight_to',
                   'spotlight_title': 'spotlight_title',
                   'spotlight_des': 'spotlight_des'},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@schema(schema=get_spotlight_schemas)
def get_spotlight(request, params):
    """
    Get office IPs
    :param request:
    :param params:
    :return:
    """
    if request.method == 'GET':
        # payload = utils.get_payload(request.GET, get_spotlight_schemas['properties'])
        spotlight_article_items = Article.objects.filter(spotlight=True, spotlight_to__gte=timezone.now().date(),
                                                 spotlight_from__lte=timezone.now().date())
        spotlight_list = [{'category': 'Article', 'item_id': spotlight_item.article_id,
                           'spotlight_image': spotlight_item.spotlight_image.url,
                           'spotlight_from': spotlight_item.spotlight_from,
                           'spotlight_to': spotlight_item.spotlight_to,
                           'spotlight_title': spotlight_item.title, }
                          for spotlight_item in spotlight_article_items]
        spotlight_post_items = Post.objects.filter(spotlight=True, spotlight_to__gte=timezone.now().date(),
                                                         spotlight_from__lte=timezone.now().date())
        spotlight_post_list = [{'category': 'Post', 'item_id': spotlight_item.post_id,
                                'spotlight_image': spotlight_item.spotlight_image.url,
                           'spotlight_from': spotlight_item.spotlight_from,
                           'spotlight_to': spotlight_item.spotlight_to,
                           'spotlight_title': spotlight_item.title, }
                          for spotlight_item in spotlight_post_items]
        ret = dict(error=0, spotlight_article=spotlight_list,spotlight_post =spotlight_post_list)
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)


get_knowledge = {
    'properties': {'knowledge_ids': 'knowledge_ids', 'name': 'name'},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
    'list_args': ['knowledge_ids'],
}

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@schema(schema=get_knowledge)
def get_knowledge(request, params):
    if request.method == 'GET':
        knowledge_ids = request.GET.getlist('knowledge_ids[]')
        if knowledge_ids:
            knowledge_objects = Knowledge.objects.filter(knowledge_id__in=knowledge_ids)
            knowledges_list = [utils.obj_to_dict(knowledge) for knowledge in knowledge_objects]
            ret = {'error': 0, 'knowledges': knowledges_list}
        else:
            payload = utils.get_payload(request.GET, get_article_schemas['properties'])
            ret = utils.get_data_in_page_and_fields(Knowledge, 'knowledge', payload, request.GET)
        
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)



get_article_public_schemas = {
    'properties': {'ip_address': 'ip_address', 'web_browser': 'web_browser', 'article_id': 'article_id',
                   'device': 'device'},
    'required': ['article_id'],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes(( TokenAuthentication,))
@schema(schema=get_article_public_schemas)
def api_get_article_details(request, params):
    article_id = params.get('article_id')
    article = Article.objects.filter(article_id=article_id).first()
    if request.user.is_authenticated:
        ret = dict(error=0, article=article.article_to_dict(get_full=True))
        return JsonResponse(data=ret)
    else:
        device_params = params.get('device')
        browser_params = params.get('web_browser')
        ip_params = params.get('ip_address')
        user_public = get_user_public(device_params, browser_params, ip_params)
        reading_list, created = ReadingList.objects.get_or_create(public_user=user_public)
        exists_in_reading_list = reading_list.read_articles.filter(id=article.id).exists()
        if reading_list.remain <=0 :
            if exists_in_reading_list:
                ret = dict(error=0, article=article.article_to_dict(get_full=True,get_full_audio=False))
                return JsonResponse(data=ret)
            else:
                ret = dict(error=0, article=article.article_to_dict(get_full=False,get_full_audio=False))
                return JsonResponse(data=ret)
        else:
            if not exists_in_reading_list:
                reading_list.remain -=1
                reading_list.read_articles.add(article)
                reading_list.save()
            ret =dict(error=0, article=article.article_to_dict(get_full=True))
            return JsonResponse(data=ret)


def get_user_public(device, browser, ip):
    if device is not None:
        device_objects, created = Device.objects.get_or_create(custom_fingerprint=device)
    if browser is not None:
        web_browser_objects, created = WebBrowser.objects.get_or_create(custom_fingerprint=browser)
    if ip is not None:
        ip_object, created = IPObject.objects.get_or_create(ip_address=ip)
    user_public, created = PublicUser.objects.get_or_create(web_browser=web_browser_objects)
    if created:
        if device is not None:
            user_public.device = device_objects
        if ip is not None:
            user_public.ip = ip_object
        user_public.save()
    return user_public

get_article_knowledge_type = {
    'properties': {'knowledge_type_id': 'knowledge_type_id'},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@schema(schema=get_article_knowledge_type)
def get_article_knowledge_type(request, params):
    if request.method == 'GET':
        if 'knowledge_type_id' in params:
            knowledge_type_id = params.get('knowledge_type_id')
            knowledge_type = KnowledgeType.objects.get(knowledge_type_id=knowledge_type_id)
            knowledge_objects = Knowledge.objects.filter(knowledge_types=knowledge_type)
            articles = Article.objects.filter(knowledge__in=knowledge_objects)
            articles_list = [utils.obj_to_dict(article) for article in articles]
            ret = {'error': 0, 'articles': articles_list}
        else:
            payload = utils.get_payload(request.GET, get_article_schemas['properties'])
            ret = utils.get_data_in_page_and_fields(Article, 'article', payload, request.GET)
        
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)
    
get_spotlight_schemas = {
'properties': {'category': 'category', 'item_id': 'item_id', 'spotlight_image': 'spotlight_image',
                'spotlight_from': 'spotlight_from', 'spotlight_to': 'spotlight_to',
                'spotlight_title': 'spotlight_title',
                'spotlight_des': 'spotlight_des'},
'required': [],
'bool_args': [],
'int_args': [],
'float_args': [],
}


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
@schema(schema=get_spotlight_schemas)
def get_spotlight(request, params):
    """
    Get office IPs
    :param request:
    :param params:
    :return:
    """
    if request.method == 'GET':
        # payload = utils.get_payload(request.GET, get_spotlight_schemas['properties'])
        spotlight_article_items = Article.objects.filter(spotlight=True, spotlight_to__gte=timezone.now().date(),
                                                 spotlight_from__lte=timezone.now().date())
        spotlight_list = [{'category': 'Article', 'item_id': spotlight_item.article_id,
                           'spotlight_image': spotlight_item.spotlight_image.url,
                           'spotlight_from': spotlight_item.spotlight_from,
                           'spotlight_to': spotlight_item.spotlight_to,
                           'spotlight_title': spotlight_item.title, }
                          for spotlight_item in spotlight_article_items]
        spotlight_post_items = Post.objects.filter(spotlight=True, spotlight_to__gte=timezone.now().date(),
                                                         spotlight_from__lte=timezone.now().date())
        print(spotlight_post_items)
        spotlight_post_list = [{'category': 'Post', 'item_id': spotlight_item.post_id,
                                'spotlight_image': spotlight_item.spotlight_image.url,
                           'spotlight_from': spotlight_item.spotlight_from,
                           'spotlight_to': spotlight_item.spotlight_to,
                           'spotlight_title': spotlight_item.title, }
                          for spotlight_item in spotlight_post_items]
        ret = dict(error=0, spotlight_article=spotlight_list,spotlight_post =spotlight_post_list)
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)
    
