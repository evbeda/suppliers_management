from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.core.exceptions import PermissionDenied
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.urls import (
    reverse_lazy,
)

from invoices_app.models import Invoice
from supplier_app.models import Address, TaxPayer
from users_app import CAN_VIEW_ALL_INVOICES_PERM, CAN_VIEW_ALL_TAXPAYERS_PERM


class IsUserCompanyInvoice(UserPassesTestMixin):

    def test_func(self):
        if not self.request.user.is_active:
            return False

        if self.request.user.has_perm(CAN_VIEW_ALL_INVOICES_PERM):
            return True

        invoice = get_object_or_404(Invoice, id=self.kwargs.get('pk'))

        taxpayer = invoice.taxpayer
        company = taxpayer.company
        companyuserpermission = \
            self.request.user.companyuserpermission_set.filter(
                company=company
            )
        if companyuserpermission:
            return True
        else:
            return False


class TaxPayerPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        
        if not self.request.user.is_active:
            return False

        if self.request.user.has_perm(CAN_VIEW_ALL_TAXPAYERS_PERM):
            return True

        taxpayer = get_object_or_404(TaxPayer, id=self.kwargs.get('taxpayer_id'))
        company = taxpayer.company
        companyuserpermission = \
            self.request.user.companyuserpermission_set.filter(
                company=company
            )
        if companyuserpermission:
            return True
        else:
            return False


class UserLoginPermissionRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not self.has_permission():
            return self.handle_no_authorization()
        return super().dispatch(request, *args, **kwargs)

    def handle_no_authorization(self):
        if self.request.user.email.endswith('@eventbrite.com'):
            return redirect(reverse_lazy('ap-taxpayers'))
        else:
            return redirect(reverse_lazy('supplier-home'))
