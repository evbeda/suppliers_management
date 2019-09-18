from django.conf.urls import url
from .views import (
    SupplierLoginView,
    SupplierLogoutView,
    ErrorLoginView
)

urlpatterns = [
    url(r'^$', SupplierLoginView.as_view(), name='login'),
    url(r'^logout$', SupplierLogoutView.as_view(), name='logout'),
    url(r'^error/invalidemail', ErrorLoginView.as_view(), name="login-error"),
    ]
