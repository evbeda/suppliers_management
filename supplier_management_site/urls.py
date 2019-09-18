from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^suppliersite/', include('supplier_app.urls')),
    url(r'^apsite/', include('AP_app.urls')),
    url(r'^', include('users_app.urls')),
    url('', include('social_django.urls', namespace='social'))
)
