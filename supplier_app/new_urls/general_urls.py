from django.conf.urls import url, include

from supplier_app.views import (
    EditAddressView,
    EditBankAccountView,
    EditTaxpayerView,
    SupplierDetailsView,
    TaxpayerCommentView,
    EditContactInformationView,
    GeneratePdf
)

taxpayer_pattern = [
    url(r'^$', SupplierDetailsView.as_view(), name='supplier-details'),
    url(
        r'^address/(?P<address_id>[0-9]+)$',
        EditAddressView.as_view(),
        name='address-update'
    ),
    url(
        r'^contact/(?P<contact_id>[0-9]+)$',
        EditContactInformationView.as_view(),
        name='contact-update'
    ),
    url(
        r'^bank_account/(?P<bank_id>[0-9]+)$',
        EditBankAccountView.as_view(),
        name='bank-account-update'
    ),
    url(
        r'^comment$',
        TaxpayerCommentView.as_view(),
        name='taxpayer-comment'
    ),
    url(r'^edit/$', EditTaxpayerView.as_view(), name='taxpayer-update'),
    url(r'^pdf/', GeneratePdf.as_view(), name='pdf-web'),
]

urlpatterns = [
    url(r'^taxpayer/(?P<taxpayer_id>[0-9]+)/', include(taxpayer_pattern)),
]
