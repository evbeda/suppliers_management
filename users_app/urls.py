from django.conf.urls import url
from .views import (
    SupplierLoginView,
    SupplierLogoutView,
)

urlpatterns = [
    url(r'^$', SupplierLoginView.as_view(), name='login'),
    url(r'^logout$', SupplierLogoutView.as_view(), name='logout'),
]
