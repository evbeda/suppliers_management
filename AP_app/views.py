from django.views.generic import TemplateView
from django.views.generic.list import ListView

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from invoices_app.models import Invoice

from . import ALLOWED_AP_ACCOUNTS


class IsApUser(UserPassesTestMixin):
    login_url = 'login-error'

    def test_func(self):
        return self.request.user.email in ALLOWED_AP_ACCOUNTS
        # return self.request.user.email.endswith('@eventbrite.com')


class APHome(LoginRequiredMixin, IsApUser, TemplateView):
    template_name = 'AP_app/ap-home.html'


class InvoiceListView(LoginRequiredMixin, IsApUser, ListView):
    template_name = 'AP_app/invoice-list.html'
    model = Invoice

    def get_queryset(self):
        queryset = Invoice.objects.filter(status='NEW')
        return queryset
