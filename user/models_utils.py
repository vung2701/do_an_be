from django.http import JsonResponse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils import timezone
from my_utils import email
from my_utils.models import Template
from . import models
from .tokens import account_activation_token
from django.contrib.auth.models import Group
import secrets
import string


def send_registration_email(base_user):
    recipient_list = [base_user.email]
    uid = urlsafe_base64_encode(force_bytes(base_user.email))
    token = account_activation_token.make_token(base_user)

    email_subject = 'ITV Registration - Email Verification'
    email_body_tpl = Template.objects.filter(name='registration_email.body').first()
    email_body_txt = email_body_tpl.text.format(name=base_user.first_name,
                                                link=f'/api/v1/user/verify/{uid}?token={token}')
    email_body_html_tpl = Template.objects.filter(name='registration_email.html_body').first()
    email_body_html = email_body_html_tpl.text.format(name=base_user.first_name,
                                                      link=f'/api/v1/user/verify/{uid}?token={token}')
    ret = email.send_email(recipient_list=recipient_list, subject=email_subject, email_body=email_body_txt,
                           email_body_html=email_body_html)
    return ret


def get_or_create_base_user(instance, password=None, is_active=True):
    if not instance.base_user:
        normal_user_group = Group.objects.get(name=models.UserRole.user)

        base_user, created = models.AuthUser.objects.get_or_create(
            email=instance.email,
            defaults=dict(username=instance.email, first_name=instance.first_name, last_name=instance.last_name,
                          is_active=False)
        )
        if password:
            base_user.set_password(password)
            base_user.save()

        if created:
            instance.base_user = base_user
            instance.base_user.groups.add(normal_user_group)
            instance.save()
            send_registration_email(instance.base_user)
        else:
            instance.is_active = False
            instance.save()
    return instance.base_user


def create_new_user(*args, **kwargs):
    student = models.Student.objects.filter(student_id=kwargs.get('student_id')).first()
    user, created = models.User.objects.get_or_create(
        first_name=kwargs.get('first_name'),
        last_name=kwargs.get('last_name'),
        email=kwargs.get('email'),
        student=student
    )

    get_or_create_base_user(user, password=kwargs.get('password1'))

    instance = user

    profile, created = models.Profile.objects.get_or_create(user=instance)
    # profile.base_user = AuthUser.objects.filter(id=instance.base_user).first()
    profile.base_user = instance.base_user
    profile.first_name = instance.first_name
    profile.last_name = instance.last_name
    profile.email = instance.email
    profile.created_on = timezone.now()
    profile.student = student
    profile.save()
    return user


def activate_user(uidb64, token):
    try:
        email = force_str(urlsafe_base64_decode(uidb64))
        user = models.AuthUser.objects.filter(email=email).first()
    except(TypeError, ValueError, OverflowError):
        user = None
    if user and user.is_active:
        return True
    if user is not None and account_activation_token.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
            related_user = models.User.objects.filter(base_user=user).first()
            if related_user:
                related_user.is_active = True
                related_user.save()
        return True
    else:
        return False


def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


def authenticate_user(email, first_name=None, last_name=None):
    # Kiểm tra xem người dùng đã tồn tại trong hệ thống hay chưa
    first_name = first_name or email
    last_name = last_name or ''

    auth_user, created = models.AuthUser.objects.get_or_create(
        email=email,
        defaults=dict(username=email, first_name=first_name, last_name=last_name, is_active=True)
    )
    if created:
        normal_user_group = models.Group.objects.get(name=models.BAWUserRole.user)
        auth_user.groups.add(normal_user_group)
        auth_user.set_password(generate_password())
        auth_user.save()
        auth_user.password = auth_user.password
        auth_user.save(update_fields=['password'])
    user, created = models.User.objects.get_or_create(
        email=email,
        defaults=dict(first_name=first_name, last_name=last_name, base_user=auth_user, is_active=True)
    )
    profile, created = models.Profile.objects.get_or_create(user=user, defaults=dict(created_on=timezone.now()))
    profile.base_user = user.base_user
    profile.first_name = user.first_name
    profile.last_name = user.last_name
    profile.email = user.email
    profile.save()
    return auth_user
