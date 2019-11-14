from django.conf.urls import url

from invoices_app.views import SupplierInvoiceCreateView

urlpatterns = [
    url(
        r'^taxpayer/(?P<taxpayer_id>[0-9]+)/invoice/$',
        SupplierInvoiceCreateView.as_view(),
        name='invoice-create',
    ),
]
