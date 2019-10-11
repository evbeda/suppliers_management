from unittest import TestCase

from parameterized import parameterized

from invoices_app import INVOICE_STATUS


def invoice_status_lookup(status_value):
    for (key, value) in INVOICE_STATUS:
            if status_value == value:
                return key
