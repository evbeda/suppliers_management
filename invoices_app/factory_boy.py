from datetime import datetime
import factory

from invoices_app.models import (
    Invoice,
)


class InvoiceFactory(factory.django.DjangoModelFactory):
    invoice_date = factory.LazyFunction(datetime.now)
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

