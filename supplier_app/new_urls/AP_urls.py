from django.conf.urls import url, include

from supplier_app.views import (
    ApTaxpayers,
    CompanyCreatorView,
    CompanyListView,
    TaxpayerHistory,
    change_taxpayer_status,
    company_invite,
)

from users_app.views import (
    AdminList,
    change_ap_permission,
    CreateAdmin,
    FormWizardView,
)


company_pattern = [
    url(r'^$', CompanyListView.as_view(), name='company-list'),
    url(r'^create$', CompanyCreatorView.as_view(), name='company-create'),
    url(r'^invite$', company_invite, name='company-invite'),
    url(r'^pagin/', FormWizardView.as_view(), name='paging'),
]

taxpayer_pattern = [
    url(r'^history/$', TaxpayerHistory.as_view(), name='taxpayer-history'),
    url(r'^status/$', change_taxpayer_status, name='handle-taxpayer-status'),
]

admins_pattern = [
    url(r'^$', AdminList.as_view(), name='manage-admins'),
    url(r'^create/$', CreateAdmin.as_view(), name='create-admin'),
    url(r'^(?P<pk>[0-9]+)/change-ap-permission$', change_ap_permission, name='change-ap-permission'),
]

urlpatterns = [
    url(r'^$', ApTaxpayers.as_view(), name='ap-taxpayers'),
    url(r'^admin/', include(admins_pattern)),
    url(r'^company/', include(company_pattern)),
    url(r'^taxpayer/(?P<taxpayer_id>[0-9]+)/', include(taxpayer_pattern)),
]

# AP
# /ap
# /company
# /company/create
# /taxpayer/:id/status/
# /taxpayer/:id/history
