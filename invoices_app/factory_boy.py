from datetime import datetime
import factory

from invoices_app.models import (
    InvoiceArg,
    Invoice,
)


class InvoiceFactory(factory.django.DjangoModelFactory):
    invoice_date = factory.LazyFunction(datetime.now)
    po_number = '98876'
    invoice_file = 'test.pdf'
    currency = 'ARS'

    class Meta:
        model = Invoice


class InvoiceArgentinaFactory(InvoiceFactory):

    class Meta:
        model = InvoiceArg

    invoice_type = 'A'
    invoice_number = '1234'
    net_amount = '4000'
    vat = '1200'
    total_amount = '5200'
