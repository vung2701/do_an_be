from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from knowledge import models
from my_utils.schema import schema

knowledge_type_schemas = {
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
@schema(schema=knowledge_type_schemas)
def get_all_type(request, params):
    if request.method == 'GET':
        knowledge_types = models.KnowledgeType.objects.all()
        ret = {
            'error': 0,
            'knowledge_types': [knowledge_type.to_dict() for knowledge_type in knowledge_types]
        }
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)
    

get_knowledge_schemas = {
    'properties': {'knowledge_type_id': 'knowledge_type_id'},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}



@csrf_exempt
@api_view(['GET'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
@schema(schema=get_knowledge_schemas)
def get_knowledge(request, params):
    if request.method == 'GET':
        knowledge_type_id = params.get('knowledge_type_id')
        if knowledge_type_id:
            knowledge_type = models.KnowledgeType.objects.filter(knowledge_type_id=knowledge_type_id).first()
            if knowledge_type:
                knowledges = models.Knowledge.objects.filter(knowledge_type=knowledge_type)
                knowledge_list = [knowledge.to_dict() for knowledge in knowledges]
                return JsonResponse({'error': 0, 'knowledges': knowledge_list})
            else:
                return JsonResponse({'error': 'Knowledge type not found'}, status=404)
        else:
            knowledges = models.Knowledge.objects.all()
            knowledge_list = [knowledge.to_dict() for knowledge in knowledges]
            return JsonResponse({'error': 0, 'knowledges': knowledge_list})
    else:
        return HttpResponse(status=403)
