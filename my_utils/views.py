from django.shortcuts import render

import os

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action

from . import utils, models
from .schema import schema, empty_schemas
# from .authentication import SessionAuthentication, TokenAuthentication
# from .permissions import IsAuthenticated
# from .decorators import avt_permission_required

# Create your views here.
upload_file_schemas = {
    'properties': {},
    'required': [], 'bool_args': [], 'int_args': [], 'float_args': [],
}


@csrf_exempt
@api_view(['POST'])
# @authentication_classes((SessionAuthentication, TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
# @avt_permission_required(groups=['admin'],perm=['avtutils.upload_file.create'])
@schema(schema=upload_file_schemas)
def upload_file(request, params, module):
    """
    Get office IPs
    :param request:
    :param params:
    :param module:
    :return:
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse(status=403, data={'error': 1403, 'message': 'Forbidden'})
        owner = request.user if request.user.is_authenticated else None

        up_file = request.FILES['file']
        file_name = ''.join([c for c in up_file.name if c.isalpha() or c.isdigit() or c == '.'])
        # add random string to ignore duplicate
        file_base, file_extension = file_name.rsplit('.', 1)
        file_name = f"{file_base}_{utils.get_random_string(8)}{timezone.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
        file_dir = os.path.join(settings.MEDIA_ROOT, module)
        os.makedirs(file_dir, exist_ok=True)
        file_path = os.path.join(settings.MEDIA_ROOT, module, file_name)
        destination = open(file_path, 'wb+')
        for chunk in up_file.chunks():
            destination.write(chunk)
        destination.close()
        uploaded_file = models.UploadFile.objects.create(name=file_name, owner=owner, file=F'{module}/{file_name}')
        return JsonResponse(status=200, data={'error': 0, module: f'{uploaded_file.file}'})
    else:
        return JsonResponse(status=400, data={'error': 'Bad request'})


@csrf_exempt
@api_view(['GET'])
# @authentication_classes((SessionAuthentication, TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
@schema(schema=empty_schemas)
def refresh_token(request, params):
    # token = Token.objects.filter(user=request.user).first()
    # return JsonResponse(data={'token': token.key})
    # token = Token.objects.filter(user=request.user).first()
    return JsonResponse(data={'token': request.auth.pk})

