import ast
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes
from my_utils.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q

from my_utils import utils
from post.models import Post
from user.models import User

from . import models
from my_utils.schema import schema

language_code_schemas = {
    'properties': {},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}

@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
@schema(schema=language_code_schemas)
def get_all_language(request, params):
    if request.method == 'GET':
        languages = models.LanguageCode.objects.all()
        ret = {
            'error': 0,
            'languages': [language.to_dict() for language in languages]
        }
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)
    

get_src_code_schemas = {
    'properties': {'language_ids': 'language_ids', 'src_code_id': 'src_code_id',
                   'name': 'name', 'content': 'content', 'post_id': 'post_id', 'created_by': 'created_by', 'search' : 'search'},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}

@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
# @permission_classes((IsAuthenticated,))
@schema(schema=get_src_code_schemas)
def get_src_code(request, params):
    if request.method == 'GET':
        if params.get('src_code_id') is not None:
            srcCode = models.SrcCode.objects.filter(src_code_id=params.get('src_code_id')).first()
            ret = dict(error=0, src_code=utils.obj_to_dict(srcCode))
            return JsonResponse(data=ret)
        if params.get('language_ids'):
            language_id = params.get('language_ids')
            language = models.LanguageCode.objects.filter(id=language_id).first()
            if language:
                search = params.get('search') or None
                user_search_condition = Q(created_by__username__icontains=search)
                name_search_condition = Q(name__icontains=search)
                srcCodes = models.SrcCode.objects.filter(user_search_condition | name_search_condition, languages=language)
                ret = utils.get_data_in_page_and_fields(srcCodes, 'src_code', {}, request.GET)
                return JsonResponse(data=ret)
            else:
                return JsonResponse({'error': 'Language not found'}, status=404)
        else:
            payload = utils.get_payload(request.GET, get_src_code_schemas['properties'])
            ret = utils.get_data_in_page_and_fields(models.SrcCode, 'src_code', payload, request.GET)
            return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)


@csrf_exempt
@api_view(['POST'])
@authentication_classes((TokenAuthentication,SessionAuthentication))
@schema(schema=get_src_code_schemas)
def create_update_src_code(request, params):
    if request.method == 'POST':
        try:
            name = params.get('name')
            content = params.get('content')
            post_id = params.get('post_id')
            language_ids = params.get('language_ids') and ast.literal_eval(params.get('language_ids')) or []
            
            if not params.get('src_code_id'):
                src_code = models.SrcCode.objects.create(
                    name=name,
                    content=content,
                    created_by=request.user
                )
                if language_ids:
                    languages = models.LanguageCode.objects.filter(id__in=language_ids)
                    src_code.languages.set(languages)
                if post_id:
                    post = Post.objects.get(post_id=post_id)
                    post.src_code.add(src_code)
            else:
                src_code_id = params.get('src_code_id')
                src_code = models.SrcCode.objects.get(src_code_id=src_code_id)
                src_code.name = name
                src_code.content = content
                src_code.modified_on = timezone.now()
                src_code.languages.clear()
                for language_id in language_ids:
                    language = models.LanguageCode.objects.get(id=language_id)
                    src_code.languages.add(language)
                src_code.save()
                
                if post_id:
                    post = Post.objects.get(post_id=post_id)
                    post.src_code.add(src_code)
                
            ret = dict(error=0, src_code=utils.obj_to_dict(src_code))
            return JsonResponse(data=ret)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
@schema(schema=get_src_code_schemas)
def delete_srccode(request, params):
    if request.method == 'POST':
        base_user = request.user
        if not base_user.user:
            return JsonResponse({'error': 'Invalid user'}, status=403)
        id = params.get('src_code_id')
        srcCode = models.SrcCode.objects.filter(src_code_id=id).first()
        if not srcCode:
            return JsonResponse({'error': 'Invalid delete id'}, status=403)
        if srcCode.created_by != base_user:
            return JsonResponse(status=403, data={'error': 'You do not have permission to delete.'})
        srcCode.delete()
        ret = dict(error=0, message='Delete successfull!')
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)
    
       