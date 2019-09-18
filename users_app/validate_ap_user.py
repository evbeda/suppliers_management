from django.shortcuts import redirect
from django.urls import reverse

USER_FIELDS = ['email']


def allowed_email_for_admin(email):
    return email.endswith('@eventbrite.com')


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))

    if not fields:
        return

    if backend.name == 'google-oauth2' and not allowed_email_for_admin(fields['email']):
        return redirect(reverse('login-error'), *args, permanent=False, **kwargs)

    return {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }
