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
    if backend == GOOGLE_OAUTH2_SOCIAL_DJANGO_BACKEND and not user.is_ap_buyer:
        buyer_group = Group.objects.get(name='ap_buyer')
        user.groups.add(buyer_group)
    return {
            'is_new': is_new,
            'user': user
        }


def check_user_backend(is_new, user, *args, **kwargs):
    backend = kwargs['backend'].name
    user_email = kwargs['details']['email']
    if backend == GOOGLE_OAUTH2_SOCIAL_DJANGO_BACKEND and not User.objects.filter(email=user_email).exists():
        if kwargs["response"].hd == 'eventbrite.com':
            user = User.objects.create_user(user_email)
        else:
            raise AuthException(backend, 'Invalid Login')
    return {
            'is_new': is_new,
            'user': user
        }
