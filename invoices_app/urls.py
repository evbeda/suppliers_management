from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'/create/$', views.CreateInvoiceView.as_view(), name='invoice-create'),
]
