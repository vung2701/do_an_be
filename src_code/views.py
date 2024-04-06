from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

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
    'properties': {'language_id': 'language_id'},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}

@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
@schema(schema=get_src_code_schemas)
def get_src_code(request, params):
    if request.method == 'GET':
        language_id = params.get('language_id')
        if language_id:
            language = models.LanguageCode.objects.filter(id=language_id).first()
            if language:
                srcCodes = models.SrcCode.objects.filter(languages=language)
                srcCodes_list = [srcCode.to_dict() for srcCode in srcCodes]
                return JsonResponse({'error': 0, 'src_codes': srcCodes_list})
            else:
                return JsonResponse({'error': 'Language not found'}, status=404)
        else:
            srcCodes = models.SrcCode.objects.all()
            srcCodes_list = [srcCode.to_dict() for srcCode in srcCodes]
            return JsonResponse({'error': 0, 'src_codes': srcCodes_list})
    else:
        return HttpResponse(status=403)

