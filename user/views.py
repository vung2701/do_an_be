# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes
from django.contrib.auth.models import User as Auth_User
from my_utils import utils
from my_utils.schema import schema

from my_utils.authentication import TokenAuthentication
# from my_utils.permissions import IsAuthenticated
# from my_utils.decorators import avt_permission_required
from .models import User, Profile
from . import models, models_utils
from datetime import datetime, timedelta
import os
import logging
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)

get_register_schemas = {
    'properties': {'user_id': 'user_id', 'first_name': 'first_name', 'last_name': 'last_name', 'student_id': 'student_id',
                   'email': 'email', 'password1': 'password1', 'password2': 'password2'},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}


@csrf_exempt
@api_view(['GET', 'POST'])
# @authentication_classes((TokenAuthentication,))
# #### @permission_classes((IsAuthenticated,))
@schema(schema=get_register_schemas)
def register(request, params):
    """
    Get office IPs
    :param request:
    :param params:
    :return:
    """
    if request.method == 'POST':
    # Try to fetch the student with the provided student_id
        student = models.Student.objects.filter(student_id=params.get('student_id')).exists()

        if not student:
            return JsonResponse(data ={
                'error': 'Student id does not exist',
                'message': 'STUDENT_NOT_EXIST'
            })
        
        existing_user = models.User.objects.filter(student__student_id=params.get('student_id')).exists()

        if existing_user:
            return JsonResponse(data = {
                'error': 'Student id is already associated with another user',
                'message': 'STUDENT_EXISTED'
            })
        user_exits = User.objects.filter(email=params.get('email')).exists()
        if user_exits:
            return JsonResponse(data={'error': 'Email is already associated with an existing account',
                                'message': 'EMAIL_EXISTED'})
        else:
            user = models_utils.create_new_user(**params)
            ret = dict(error=0, user=utils.obj_to_dict(user),
                    inform_msg='EMAIL_VERIFY')
            return JsonResponse(data=ret)
        # return HttpResponse('Please confirm your email address to complete the registration')
    else:
        return HttpResponse(status=403)


verify_email_schemas = {
    'properties': {'token': 'token'},
    'required': [], 'bool_args': [], 'int_args': [], 'float_args': [],
}


@csrf_exempt
@api_view(['GET', 'POST'])
@schema(schema=verify_email_schemas)
def verify_email(request, params, uidb64):
    """
    Get office IPs
    :param request:
    :param params:
    :return:
    """
    if request.method == 'GET':
        if models_utils.activate_user(uidb64, params.get('token')):
            # return HttpResponse('Success', status=200)
            return HttpResponseRedirect('http://localhost:5173/login')
        else:
            return HttpResponse('False to register user', status=500)
    else:
        return HttpResponse(status=403)


get_user_schemas = {
    'properties': {'user_id': 'base_user__id', 'email': 'email', 'password': 'password', 'is_active': 'is_active',
                   'first_name': 'first_name', 'last_name': 'last_name'},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
# @avt_permission_required(perm=['auth.view_user'])
@schema(schema=get_user_schemas)
def get_user(request, params):
    """
    Get office IPs
    :param request:
    :param params:
    :return:
    """
    if request.method == 'GET':
        payload = utils.get_payload(request.GET, get_user_schemas['properties'])
        payload['base_user__id'] = request.user.id
        # ret = utils.get_data_in_page_and_fields(User, 'user', payload, request.GET, )
        user = models.AuthUser.objects.filter(id=request.user.id).first()
        profile = models.Profile.objects.filter(base_user=user.id).first()
        # user_groups = user.groups.values_list('name', flat=True)
        if not user.groups.filter(name=models.UserRole.employee).exists():
            normal_user_group = models.Group.objects.get(name=models.UserRole.employee)
            user.groups.add(normal_user_group)

        user_roles = user.groups.filter(name__startswith='role_').values_list('name', flat=True)
        user_roles = [_[5:] for _ in user_roles]
        if not user:
            return HttpResponse(status=403)
        ret = dict(error=0, user=dict(
            first_name=user.first_name, last_name=user.last_name, user_id=profile.user_id_profile, role=list(user_roles), is_active=user.is_active
        ))
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)



user_login_schemas = {
    'properties': {'email': 'email', 'password': 'password', 'user_id': 'user_id'},
    'required': ['email', 'password'],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}



user_logout_schemas = {
    'properties': {},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
@schema(schema=user_logout_schemas)
def user_logout(request, params):
    if request.user and request.user.is_authenticated:
        logout(request)
        return HttpResponse('Logout success', status=200)
    else:
        return HttpResponse('Logout error', status=403)
    


get_profile_schemas = {
    'properties': {'user_id': 'user_id', 'image': 'image',
                   'first_name': 'first_name', 'last_name': 'last_name',
                   'email': 'email', 'base_user ': 'base_user',
                   'school': 'school', 'major': 'major', 'location': 'location',
                   'phone': 'phone', 'DOB': 'DOB', 'class': "class"},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}


def _get_profile(request, params):
    if request.method == 'POST':
        profile = Profile.objects.filter(user_id_profile=params.get('user_id')).first()
        if not profile:
            return JsonResponse(status=403, data=dict(error=1001, msg='User profile exception!'))

        profile.image = params.get('image')

        profile.save()
        ret = dict(error=0, profile=utils.obj_to_dict(profile))
        return JsonResponse(data=ret)
    elif request.method == 'GET':
        if params.get('user_id') is not None:
            profile = Profile.objects.filter(user_id_profile=params.get('user_id')).first()
            if request.user == profile.base_user or request.user.is_staff:
                profiles = Profile.objects.filter(user_id_profile=params.get('user_id')).first()

                ret = dict(error=0, profile=profiles.profile_to_dict())
            else:
                request_profile = {'user_id_profile': profile.user_id_profile, 'first_name': profile.first_name,
                               'last_name':profile.last_name,'image': profile.image.name, 'school': profile.school,
                                'major': profile.major, 'class': profile.student.student_class, 'student_id': profile.student.student_id}
                ret = dict(error=0, profile=request_profile)
        else:
            payload = utils.get_payload(request.GET, get_profile_schemas['properties'])
            ret = utils.get_data_in_page_and_fields(Profile, 'profile', payload, request.GET, )
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
# @avt_permission_required(perm=['user.view_profile'])
@schema(schema=get_profile_schemas)
def get_my_profile(request, params):
    params['user__base_user__id'] = request.user.id
    return _get_profile(request, params)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
# @avt_permission_required(perm=['user.view_profile'])
@schema(schema=get_profile_schemas)
def get_profile(request, params):
    return _get_profile(request, params)


@csrf_exempt
@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
# @avt_permission_required(perm=['user.change_profile'])
@schema(schema=get_profile_schemas)
def edit_profile(request, params):
    if request.method == 'POST':
        user_profile = Profile.objects.filter(user_id_profile=params.get('user_id')).first()
        if request.user.id != user_profile.base_user.id:
            return JsonResponse(status=403, data={'error': 'You do not have permission to edit this profile.'})
        user = user_profile.user
        student = user_profile.student
        auth_user = user_profile.base_user
        first_name = params.get('first_name')
        last_name = params.get('last_name')
        if first_name is not None and first_name:
            user_profile.first_name = first_name
            user.first_name = first_name
            auth_user.first_name = first_name
        else:
            return JsonResponse(status=500, data={'error': 'You cannot leave the first name blank'})
        if last_name is not None and last_name:
            user_profile.last_name = last_name
            user.last_name = last_name
            auth_user.last_name = last_name
        else:
            return JsonResponse(status=500, data={'error': 'You cannot leave the last name blank'})
        if params.get('class') is not None:
            if params.get('class'):
                user_profile.student.student_class = params.get('class')
                student.student_class =params.get('class')
        if params.get('school') is not None:
            if params.get('school'):
                user_profile.school = params.get('school')
        if params.get('major') is not None:
            if params.get('major'):
                user_profile.major = params.get('major')
        if params.get('location') is not None:
            if params.get('location'):
                user_profile.location = params.get('location')
        if params.get('phone') is not None:
            phone_value = params.get('phone', '')
            if phone_value:
                user_profile.phone = int(phone_value.strip())
        if params.get('DOB') is not None:
            if params.get('DOB'):
                user_profile.DOB = params.get('DOB')
        user_profile.save()
        student.save()
        user.save()
        auth_user.save()
        ret = dict(error=0, profile=utils.obj_to_dict(user_profile))
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)


user_image_schemas = {
    'properties': {},
    'required': [],
    'bool_args': [],
    'int_args': [],
    'float_args': [],
}
@csrf_exempt
@api_view(['POST'])
@authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
# @avt_permission_required(perm=['user.add_userimage'])
@schema(schema=user_image_schemas)
def upload_user_image(request, params):
    """
    Get office IPs
    :param request:
    :param params:
    :return:
    """
    if request.method == 'POST':
        up_file = request.FILES.get('file')
        if up_file: 
            # add random string to ignore duplicate
            file_name = ''.join([c for c in up_file.name if c.isalpha() or c.isdigit() or c == '.'])
            if models.UserImage.objects.filter(name=file_name).exists():
                # Tên file đã tồn tại, thêm một số duy nhất vào tên file
                base, extension = file_name.rsplit('.', 1)
                file_name = f"{base}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{extension}"
            file_path = os.path.join(settings.MEDIA_ROOT, 'user_image', file_name)
            destination = open(file_path, 'wb+')
            for chunk in up_file.chunks():
                destination.write(chunk)
            destination.close()
            owner = request.user if request.user.is_authenticated else None
            user_image = models.UserImage.objects.create(name=file_name, owner=owner, image=F'user_image/{file_name}')
            return JsonResponse(status=200, data={'user_image': f'{user_image.image}'})
        
        else:
                # Handle case where a file key exists but no file is uploaded
                return JsonResponse(status=400, data={'error': 'No file uploaded in the "file" field'})
    else:
        return JsonResponse(status=403, data={'error': 'function is not ready yet!'})


@csrf_exempt
@api_view(['GET', 'POST'])
# @authentication_classes((TokenAuthentication,))
# @permission_classes((IsAuthenticated,))
@schema(schema=get_profile_schemas)
def get_new_member(request, params):
    if request.method == 'GET':
        today = datetime.now()
        start_date = today.date() - timedelta(days=30)
        new_members = Profile.objects.filter(created_on__range=(start_date, today))
        project_list = [{'user_id': profile.user_id_profile,
                         'first_name': profile.first_name, 'last_name': profile.last_name,
                         'email': profile.email, 'image': profile.image.name, 'school': profile.school,
                         'major': profile.major, 'created_on': profile.created_on} for profile in
                        new_members]
        ret = dict(error=0, profile=project_list)
        return JsonResponse(data=ret)
    else:
        return HttpResponse(status=403)
