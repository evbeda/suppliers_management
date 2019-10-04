from django.conf.urls import url

from supplier_app.views import (
    ApTaxpayers,
    CompanyCreatorView,
    CompanySelectorView,
    CreatePDFFileView,
    CreateTaxPayerView,
    EditAddressView,
    EditBankAccountView,
    EditTaxpayerView,
    PDFFileView,
    SupplierDetailsView,
    SupplierHome,
    approve_taxpayer,
    refuse_taxpayer,
)

urlpatterns = [
    url(r'^ap$', ApTaxpayers.as_view(), name='ap-taxpayers'),
    url(r'^supplier$', SupplierHome.as_view(), name='supplier-home'),
    url(r'^supplier/company$', CompanySelectorView.as_view(), name='company-selector'),
    url(r'^supplier/company/create$', CompanyCreatorView.as_view(), name='company-create'),
    url(r'^supplier/taxpayer/create$', CreateTaxPayerView.as_view(), name='taxpayer-create'),
    url(r'^ap/taxpayer/(?P<taxpayer_id>[0-9]+)/details/$', SupplierDetailsView.as_view(), name='supplier-details'),
    url(r'^ap/taxpayer/(?P<taxpayer_id>[0-9]+)/details/approve$', approve_taxpayer, name='approve-taxpayer'),
    url(r'^ap/taxpayer/(?P<taxpayer_id>[0-9]+)/details/refuse$', refuse_taxpayer, name='refuse-taxpayer'),
    url(r'^files/create$', CreatePDFFileView.as_view(), name='create-file'),
    url(r'^files/$', PDFFileView.as_view(), name='show-files'),
    url(r'^ap/taxpayer/(?P<taxpayer_id>[0-9]+)/update/taxpayer_info$', EditTaxpayerView.as_view(), name='taxpayer-update'),
    url(r'^ap/taxpayer/(?P<taxpayer_id>[0-9]+)/update/address_info$', EditAddressView.as_view(), name='address-update'),
    url(r'^ap/taxpayer/(?P<taxpayer_id>[0-9]+)/update/bank_account_info$', EditBankAccountView.as_view(), name='bank-account-update'),

]
