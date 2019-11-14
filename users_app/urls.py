from django.conf.urls import url, include
from users_app.views import (
    LoginView,
    LogoutView,
    ErrorLoginView,
    set_user_language,
)

users_patterns = [
    url(r'^ap/', include('supplier_app.new_urls.AP_urls')),
    url(r'^ap/', include('invoices_app.new_urls.AP_urls')),
    url(r'^supplier/', include('supplier_app.new_urls.supplier_urls')),
    url(r'^supplier/', include('invoices_app.new_urls.supplier_urls')),
    url(r'^', include('supplier_app.new_urls.general_urls')),
    url(r'^', include('invoices_app.new_urls.general_urls')),
]

urlpatterns = [
    url(r'^$', LoginView.as_view(), name='login'),
    url(r'^logout$', LogoutView.as_view(), name='logout'),
    url(r'^login-error$', ErrorLoginView.as_view(), name='login-error'),
    url(r'^set_user_language/$', set_user_language, name='set_user_language'),
    url(r'^users/', include(users_patterns)),
]
