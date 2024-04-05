"""
Provides various authentication policies.
"""
import base64
import binascii

from django.contrib.auth import authenticate, get_user_model
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.translation import gettext_lazy as _

from rest_framework import HTTP_HEADER_ENCODING, exceptions

from rest_framework.authentication import SessionAuthentication, BaseAuthentication
from rest_framework.authentication import get_authorization_header

import logging

logger = logging.getLogger(__name__)


class TokenAuthentication(BaseAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'Bearer'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            logger.info(msg)
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            logger.info(msg)
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            logger.info(msg)
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword


def session_authentication_enforce_csrf(self, request):
    """
    Enforce CSRF validation for session based authentication.
    """

    def dummy_get_response(request):  # pragma: no cover
        return None

    # check = CSRFCheck(dummy_get_response)
    # populates request.META['CSRF_COOKIE'], which is used in process_view()
    # check.process_request(request)
    # reason = check.process_view(request, None, (), {})
    # if reason:
    #     # CSRF failed, bail with explicit error message
    #     raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)
    pass
