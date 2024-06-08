from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes
from knowledge.models import Knowledge, KnowledgeType
from my_utils.authentication import SessionAuthentication, TokenAuthentication
from my_utils import utils
from my_utils.schema import schema
from post.models import Post
from .models import  Article, Comment
from user.models import User, Profile
from django.contrib.auth.models import User as Auth_User
from django.utils import timezone
from . import filter_articles
from django.db.models import Q



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

get_article_knowledge_type = {
    'properties': {'knowledge_type_id': 'knowledge_type_id', 'search': 'search'},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}

@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@schema(schema=get_article_knowledge_type)
def get_article(request, params):
    if request.method == 'GET':
        search = params.get('search') or None
        knowledge_type_id = params.get('knowledge_type_id')
        
        if knowledge_type_id:
            knowledge_type = KnowledgeType.objects.get(knowledge_type_id=knowledge_type_id)
            knowledge_objects = Knowledge.objects.filter(knowledge_types=knowledge_type)
            if search:
                articles = Article.objects.filter(
                    (Q(created_by__username__icontains=search) | Q(title__icontains=search)),
                    knowledge__in=knowledge_objects
                )
            else:
                articles = Article.objects.filter(knowledge__in=knowledge_objects)
        else:
            if search:
                articles = Article.objects.filter(
                    Q(created_by__username__icontains=search) | Q(title__icontains=search)
                )
            else:
                payload = utils.get_payload(request.GET, get_article_schemas['properties'])
                articles = Article.objects.all()  # Retrieve all articles if no search or knowledge_type_id provided
                ret = utils.get_data_in_page_and_fields(articles, 'article', payload, request.GET)
                return JsonResponse(data=ret)

        ret = utils.get_data_in_page_and_fields(articles, 'article', {}, request.GET)
        return JsonResponse(data=ret)

    else:
        return HttpResponse(status=403)
    
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
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
               
                article.like_list.add(base_user)
                article.like_auth.add(base_user)
                article.save()
            
            ret = dict(error=0, article=utils.obj_to_dict(article))
            print(ret)

            return JsonResponse(data=ret)
        else:
            ret = dict(error=1, message='Article not found')
            return JsonResponse(status=400, data=ret)
    else:
        return HttpResponse(status=403)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((SessionAuthentication, TokenAuthentication,))
@schema(schema=get_article_schemas)
def article_unlike(request, params):
    if request.method == 'POST':
        article = Article.objects.filter(article_id=params.get('article_id')).first()
        if params.get('like_auth') != '':
            article.likes -= 1
            auth_user_profile = Profile.objects.filter(user_id_profile=params.get('like_auth')).first()
            auth_user_id = auth_user_profile.base_user_id
            base_user = Auth_User.objects.filter(id=auth_user_id).first()
            article.like_list.remove(base_user)
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
                   'parent_comment': 'parent_comment__id', 'created_by': 'created_by',
                   'created_by_first_name': 'created_by_first_name',
                   'created_by_last_name': 'created_by_last_name',
                   'created_by_image': 'created_by_image',
                   'comment_id': 'comment_id', 'like_list': 'like_list', 
                   'like_auth': 'like_auth',  },
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
        article=Article.objects.filter(article_id=params.get('parent_article_id')).first()
        base_user = Auth_User.objects.filter(id=request.user.id).first()
        user = User.objects.filter(base_user=base_user).first()
        comment = Comment.objects.create(
            title=params.get('title'),
            parent_article=article,
            description=params.get('description'),
            created_by = user
        )
        comment.created_by_first_name = comment.created_by.first_name
        comment.created_by_last_name = comment.created_by.last_name
        profile = Profile.objects.filter(user=comment.created_by).first()
        comment.created_by_image = profile.image
        comment.save()
        article.comments += 1
        article.save()
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
    ret = dict(error=0, article=article.article_to_dict(get_full=True))
    return JsonResponse(data=ret)
   
    
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
    
