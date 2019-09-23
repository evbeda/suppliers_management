from django.conf.urls import url

from .views import APHome, InvoiceListView

urlpatterns = [
    url(r'^home$', APHome.as_view(), name='ap-home'),
    url(r'^invoices$', InvoiceListView.as_view(), name='ap-invoices'),
]
