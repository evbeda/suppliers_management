# python puro

# terceros
from django.conf.urls import url
# propias

# proyecto
from .views import (
    SupplierHome,
    CreateFileView,
    CreateTaxPayerView,
    InvoiceCreateView
)

urlpatterns = [
    url(r'^home$', SupplierHome.as_view(), name='supplier-home'),
    url(r'^file/create$', CreateFileView.as_view(), name='create-file'),
    url(r'^taxpayer/create$', CreateTaxPayerView.as_view(), name='taxpayer-create'),
    url(r'^invoices/new/$', InvoiceCreateView.as_view(), name='invoice-create')
]
