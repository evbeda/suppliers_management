# python puro

# terceros
from django.conf.urls import url
# propias

# proyecto
from .views import (
    SupplierHome,
    CreatePDFFileView,
    PDFFileView,
    CreateTaxPayerView,
    InvoiceCreateView,
    InvoiceListView
)

urlpatterns = [
    url(r'^home$', SupplierHome.as_view(), name='supplier-home'),
    url(r'^files/create$', CreatePDFFileView.as_view(), name='create-file'),
    url(r'^files/$', PDFFileView.as_view(), name='show-files'),
    url(r'^taxpayer/create$', CreateTaxPayerView.as_view(), name='taxpayer-create'),
    url(r'^(?P<taxpayer_id>[0-9]+)/invoices/$', InvoiceListView.as_view(), name='supplier-invoice-list'),
    url(r'^(?P<taxpayer_id>[0-9]+)/invoices/new/$', InvoiceCreateView.as_view(), name='invoice-create')
]
