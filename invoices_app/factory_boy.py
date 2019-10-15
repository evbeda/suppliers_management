from datetime import datetime, timedelta

import factory

from invoices_app.models import Invoice


def get_due_date():
    return datetime.now() + timedelta(days=15)


class InvoiceFactory(factory.django.DjangoModelFactory):
    invoice_date = factory.LazyFunction(datetime.now)
    invoice_due_date = factory.LazyFunction(get_due_date)
    po_number = '98876'
    invoice_file = 'test.pdf'
    currency = 'ARS'
    invoice_type = 'A'
    invoice_number = '1234'
    net_amount = '4000'
    vat = '1200'
    total_amount = '5200'

    class Meta:
        model = Invoice
