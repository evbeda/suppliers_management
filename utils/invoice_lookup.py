from django.utils.translation import gettext as _
from invoices_app import INVOICE_STATUS


def invoice_status_lookup(status_value):
    for (key, value) in INVOICE_STATUS:
        if _(status_value) == value:
            return key
