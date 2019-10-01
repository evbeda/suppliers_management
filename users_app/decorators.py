from users_app import ALLOWED_AP_ACCOUNTS
from functools import wraps
from django.http import HttpResponseForbidden
from django.utils.decorators import available_attrs


def is_ap_or_403():

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if request.user.email in ALLOWED_AP_ACCOUNTS:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden('Forbidden')
        return _wrapped_view
    return decorator
