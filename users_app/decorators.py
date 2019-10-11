from functools import wraps

from django.http import HttpResponseForbidden
from django.utils.decorators import available_attrs

from invoices_app.models import Invoice
from users_app import ALLOWED_AP_ACCOUNTS


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


def is_invoice_for_user():

    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_active:
                return HttpResponseForbidden('Forbidden')

            if request.user.is_AP:
                return view_func(request, *args, **kwargs)

            invoice = Invoice.objects.filter(id=kwargs['pk'])[0]
            taxpayer = invoice.taxpayer
            company = taxpayer.company
            companyuserpermission = \
                request.user.companyuserpermission_set.filter(
                    company=company
                )
            if companyuserpermission:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden('Forbidden')


        return _wrapped_view
    return decorator
