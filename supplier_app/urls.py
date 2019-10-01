from django.conf.urls import url

from supplier_app.views import (
    ApTaxpayers,
    CreatePDFFileView,
    CreateTaxPayerView,
    PDFFileView,
    SupplierDetailsView,
    SupplierHome,
)

urlpatterns = [
    url(r'^ap$', ApTaxpayers.as_view(), name='ap-taxpayers'),
    url(r'^supplier$', SupplierHome.as_view(), name='supplier-home'),
    url(r'^supplier/taxpayer/create$', CreateTaxPayerView.as_view(), name='taxpayer-create'),
    url(r'^taxpayer/(?P<taxpayer_id>[0-9]+)/details/$', SupplierDetailsView.as_view(), name='supplier-details'),
    url(r'^files/create$', CreatePDFFileView.as_view(), name='create-file'),
    url(r'^files/$', PDFFileView.as_view(), name='show-files'),
    # url(r'^(?P<taxpayer_id>[0-9]+)/update/$', TaxPayerUpdateView.as_view(), name='supplier-update')
]
