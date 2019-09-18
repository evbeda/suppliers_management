from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class SupplierHome(LoginRequiredMixin, TemplateView):
    template_name = 'supplier_app/supplier-home.html'
    login_url = '/'
