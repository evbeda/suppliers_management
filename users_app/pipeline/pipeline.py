from django.contrib.auth.models import Group
from social_core.exceptions import AuthException
from users_app.models import User
from users_app import (
    GOOGLE_OAUTH2_SOCIAL_DJANGO_BACKEND,
    EVENTBRITE_OAUTH_SOCIAL_DJANGO_BACKEND,
)


def add_user_to_group(is_new, user, *args, **kwargs):
    backend = kwargs['backend'].name
    if is_new and backend == EVENTBRITE_OAUTH_SOCIAL_DJANGO_BACKEND:
        supplier_group = Group.objects.get(name='supplier')
        user.groups.add(supplier_group)

    return {
            'is_new': is_new,
            'user': user
        }


def check_user_backend(is_new, user, *args, **kwargs):
    backend = kwargs['backend'].name
    user_email = kwargs['details']['email']
    if backend == GOOGLE_OAUTH2_SOCIAL_DJANGO_BACKEND and not User.objects.filter(email=user_email).exists():
        raise AuthException(backend, 'Invalid Login')
    return {
            'is_new': is_new,
            'user': user
        }
