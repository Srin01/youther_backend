import uuid
from datetime import datetime

from rest_framework_jwt.compat import get_username
from rest_framework_jwt.compat import get_username_field
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.middleware import get_user
from rest_framework.request import Request
from django.utils.functional import SimpleLazyObject


def jwt_payload_handler(user):
    """Slightly customized jwt payload that include user profile picture"""

    username_field = get_username_field()
    username = get_username(user)

    payload = {
        'user_id': user.pk,
        'username': username,
        'profile_pic': user.profile_pic.url,
        'exp': datetime.utcnow() + api_settings.JWT_EXPIRATION_DELTA
    }
    if hasattr(user, 'fullname'):
        payload['fullname'] = user.fullname

    payload[username_field] = username

    return payload

# def get_user_jwt(request):
#     user = get_user(request)
#     if user.is_authenticated():
#         return user
#     try:
#         user_jwt = JSONWebTokenAuthentication().authenticate(Request(request))
#         if user_jwt is not None:
#             return user_jwt[0]
#     except:
#         pass
#     return user

# class AuthenticationMiddlewareJWT(object):
#     def process_request(self, request):
#         assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

#         request.user = SimpleLazyObject(lambda: get_user_jwt(request))