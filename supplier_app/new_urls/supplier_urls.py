from django.conf.urls import url
from supplier_app.views import (
    CreateTaxPayerView,
    SupplierHome,
    company_join,
)

urlpatterns = [
    url(r'^taxpayer/$', CreateTaxPayerView.as_view(), name='taxpayer-create'),
    url(
        r'^company/join/(?P<token>[a-f0-9]{64})$',
        company_join,
        name='company-join',
    ),
]

# Supplier
# /company/:id
# /company/:id/taxpayer/create
# /company/join/:token
