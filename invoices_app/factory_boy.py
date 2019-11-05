from datetime import datetime, timedelta
from django.core.files import File
from unittest.mock import MagicMock
import factory

from invoices_app.models import Invoice
from supplier_app.tests.factory_boy import EBEntityFactory

file_mock = MagicMock(spec=File)
file_mock.name = 'test.pdf'
file_mock.size = 50

def get_due_date():
    return datetime.now() + timedelta(days=15)


class InvoiceFactory(factory.django.DjangoModelFactory):
    invoice_date = factory.LazyFunction(datetime.now)
    invoice_due_date = factory.LazyFunction(get_due_date)
    po_number = '98876'
    invoice_file = file_mock
    currency = 'ARS'
    invoice_type = 'A'
    invoice_number = '1234'
    net_amount = '4000'
    vat = '1200'
    total_amount = '5200'
    invoice_eb_entity = factory.SubFactory(EBEntityFactory)

    class Meta:
        model = Invoice
