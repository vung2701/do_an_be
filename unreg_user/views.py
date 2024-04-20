from django.shortcuts import render

from article.models import Article
from my_utils import schema, utils
from .models import ReadingList,PublicUser,WebBrowser
import logging
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

logger = logging.getLogger(__name__)
get_unreg_user_schemas ={
    'properties':{'web_browser': 'web_browser', 'device': 'device', 'ip_objects': 'ip_objects','language':'language'
                  },
    'required' : [],
    'bool_args':[],
    'int_args':[],
    'float_args':[]
}

@csrf_exempt
@api_view(['GET','POST'])
@authentication_classes((SessionAuthentication,TokenAuthentication))
@schema(schema=get_unreg_user_schemas)
def get_readinglist(request, params):
    if request.method == 'GET':
        web = WebBrowser.objects.filter(custom_fingerprint=params.get('web_browser')).first()
        public_user = PublicUser.objects.filter(web_browser = web).first()
        readlist = ReadingList.objects.filter(public_user = public_user).first()
        read_articles_objects =  readlist.read_articles.all().values_list('id')

        payload = utils.get_payload(request.GET, get_unreg_user_schemas['properties'])
        payload['id__in'] = read_articles_objects
        payload.pop('web_browser', None)
        payload.pop('device', None)
        payload.pop('ip_objects', None)
        ret = utils.get_data_in_page_and_fields(Article, 'article', payload, request.GET, )
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=500)