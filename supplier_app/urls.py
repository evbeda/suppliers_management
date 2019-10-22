from django.conf.urls import url

from supplier_app.views import (
    ApTaxpayers,
    CompanyCreatorView,
    CompanyListView,
    CreateTaxPayerView,
    EditAddressView,
    EditBankAccountView,
    EditTaxpayerView,
    SupplierDetailsView,
    SupplierHome,
    company_invite,
    company_join,
    change_taxpayer_status,
)

urlpatterns = [
    url(r'^ap$', ApTaxpayers.as_view(), name='ap-taxpayers'),
    url(r'^supplier$', SupplierHome.as_view(), name='supplier-home'),
    url(r'^ap/company/create$', CompanyCreatorView.as_view(), name='company-create'),
    url(r'^companies$', CompanyListView.as_view(), name='company-list'),
    url(r'^company/invite$', company_invite, name='company-invite'),
    url(r'^company/join/(?P<token>[a-f0-9]{64})$', company_join, name='company-join'),
    url(r'^supplier/taxpayer/create$', CreateTaxPayerView.as_view(), name='taxpayer-create'),
    url(r'^taxpayer/(?P<taxpayer_id>[0-9]+)/$', SupplierDetailsView.as_view(), name='supplier-details'),
    url(r'^ap/taxpayer/(?P<taxpayer_id>[0-9]+)/status/$', change_taxpayer_status, name='handle-taxpayer-status'),
    url(r'^ap/taxpayer/update/taxpayer_info/(?P<taxpayer_id>[0-9]+)$', EditTaxpayerView.as_view(), name='taxpayer-update'),
    url(r'^ap/taxpayer/address_info/(?P<address_id>[0-9]+)/update$', EditAddressView.as_view(), name='address-update'),
    url(r'^ap/taxpayer/bank_account_info/(?P<bank_id>[0-9]+)/update$', EditBankAccountView.as_view(), name='bank-account-update'),

]
