from django.views.generic.list import ListView
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from pure_pagination.mixins import PaginationMixin

from invoices_app.forms import InvoiceForm
from invoices_app.models import Invoice, InvoiceArg
from supplier_app.models import TaxPayer
from users_app.decorators import is_ap_or_403
from invoices_app import (
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_NEW,
    INVOICE_STATUS_REJECTED
)


class InvoiceListView(
    LoginRequiredMixin,
    PaginationMixin,
    ListView
):
    template_name = 'AP_app/invoice-list.html'
    model = Invoice
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_AP'] = self.request.user.is_AP
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_AP:
            queryset = Invoice.objects.filter(status=INVOICE_STATUS_NEW).order_by('id')
        else:
            queryset = Invoice.objects.filter(user=user)
        return queryset


class SupplierInvoiceListView(LoginRequiredMixin, PaginationMixin, ListView):
    template_name = 'supplier_app/invoice-list.html'
    model = Invoice
    paginate_by = 10

    def get_queryset(self):
        tax_payer = get_object_or_404(TaxPayer, id=self.kwargs['taxpayer_id'])
        queryset = Invoice.objects.filter(taxpayer=tax_payer.id).order_by('id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer_id'] = self.kwargs['taxpayer_id']
        return context


class SupplierInvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'supplier_app/invoices_form.html'

    def get_success_url(self):
        return reverse_lazy('supplier-invoice-list', kwargs={'taxpayer_id': self.kwargs['taxpayer_id']})

    def form_valid(self, form):
        form.instance.user = self.request.user
        tax_payer = get_object_or_404(TaxPayer, id=self.kwargs['taxpayer_id'])
        form.instance.taxpayer = tax_payer
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer_id'] = self.kwargs['taxpayer_id']
        return context


class InvoiceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = InvoiceArg
    form_class = InvoiceForm
    template_name = 'supplier_app/invoices_form.html'
    redirect_field_name = None

    def get_success_url(self):
        taxpayer_id = self.kwargs.get('taxpayer_id')
        if taxpayer_id:
            return reverse_lazy(
                'supplier-invoice-list',
                kwargs={'taxpayer_id': taxpayer_id}
            )
        else:
            return reverse_lazy(
                'invoices-list',
            )

    def user_has_permission(self):
        if self.request.user.is_AP:
            return True
        else:
            # Only allow supplier to edit the invoice if it's status is 'CHANGES REQUEST'
            invoice = get_object_or_404(InvoiceArg, id=self.kwargs['pk'])
            return invoice.status == 'CHANGES REQUEST'

    def get_test_func(self):
        return self.user_has_permission

    def get_login_url(self):
        taxpayer_id = self.kwargs.get('taxpayer_id')
        if taxpayer_id:
            return reverse('supplier-invoice-list', kwargs={'taxpayer_id': taxpayer_id})
        else:
            return reverse('invoices-list')


@is_ap_or_403()
def approve_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.status = INVOICE_STATUS_APPROVED
    invoice.save()
    return redirect('invoices-list')


@is_ap_or_403()
def reject_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.status = INVOICE_STATUS_REJECTED
    invoice.save()
    return redirect('invoices-list')
