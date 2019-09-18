from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView


class SupplierLoginView(TemplateView):
    template_name = 'registration/login.html'


class SupplierLogoutView(LogoutView):
    pass
