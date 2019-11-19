from django.conf.urls import url, include

from supplier_app.views import (
    EditAddressView,
    EditBankAccountView,
    EditTaxpayerView,
    SupplierDetailsView,
    SupplierHome,
    TaxpayerCommentView,
)

taxpayer_pattern = [
    url(r'^$', SupplierDetailsView.as_view(), name='supplier-details'),
    url(
        r'^address/(?P<address_id>[0-9]+)$',
        EditAddressView.as_view(),
        name='address-update'
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
]

urlpatterns = [
    url(r'^taxpayer/(?P<taxpayer_id>[0-9]+)/', include(taxpayer_pattern)),
    url(r'^me', SupplierHome.as_view(), name='home'),
]
