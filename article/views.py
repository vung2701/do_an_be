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