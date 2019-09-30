from django.conf.urls import url

from supplier_app.views import (
    SupplierHome,
    CreateTaxPayerView,
    ApTaxpayers,
    CreatePDFFileView,
    PDFFileView,
)

urlpatterns = [
    url(r'^ap$', ApTaxpayers.as_view(), name='ap-taxpayers'),
    url(r'^supplier$', SupplierHome.as_view(), name='supplier-home'),
    url(r'^supplier/taxpayer/create$', CreateTaxPayerView.as_view(), name='taxpayer-create'),
    # url(r'^(?P<taxpayer_id>[0-9]+)/update/$', TaxPayerUpdateView.as_view(), name='supplier-update')
    url(r'^files/create$', CreatePDFFileView.as_view(), name='create-file'),
    url(r'^files/$', PDFFileView.as_view(), name='show-files'),
]
