
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin
)
from django.core.validators import ValidationError
from django.http import HttpResponseBadRequest

from django.urls import (
    reverse,
    reverse_lazy
)
from django_filters.views import FilterView
from django.views.generic.list import ListView
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView
from django.shortcuts import get_object_or_404, redirect
from pure_pagination.mixins import PaginationMixin

from invoices_app.forms import InvoiceForm
from invoices_app.models import (
    Invoice,
    Comment
)

from supplier_app.models import TaxPayer
from users_app.decorators import is_ap_or_403
from invoices_app import INVOICE_STATUS
from invoices_app import (
    INVOICE_STATUS,
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_NEW,
    INVOICE_STATUS_REJECTED,
    INVOICE_STATUS_CHANGES_REQUEST,
    INVOICE_STATUS_PAID,
)
from invoices_app.filters import InvoiceFilter
from supplier_app.models import (
    TaxPayer,
    Address,
    COUNTRIES,
)
from utils import send_email


class InvoiceListView(
    LoginRequiredMixin,
    PaginationMixin,
    FilterView
):
    # queryset = Invoice.objects.filter()
    template_name = 'invoices_app/invoice-list.html'
    model = Invoice
    paginate_by = 10
    filterset_class = InvoiceFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_AP'] = self.request.user.is_AP
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_AP:
            queryset = Invoice.objects.filter().defer('invoice_file').order_by('id')
        else:
            queryset = Invoice.objects.filter(user=user).defer('invoice_file')
        return queryset


class SupplierInvoiceListView(LoginRequiredMixin, PaginationMixin, ListView):
    template_name = 'supplier_app/invoice-list.html'
    model = Invoice
    paginate_by = 10

    def get_queryset(self):
        tax_payer = get_object_or_404(TaxPayer, id=self.kwargs['taxpayer_id'])
        queryset = Invoice.objects.filter(taxpayer=tax_payer.id).defer('invoice_file').order_by('id')
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
        taxpayer = get_object_or_404(TaxPayer, id=self.kwargs['taxpayer_id'])
        form.instance.taxpayer = taxpayer
        invoice_number = form.cleaned_data['invoice_number']
        if Invoice.objects.filter(taxpayer=taxpayer.id, invoice_number=invoice_number).exists():
            form.errors['invoice_number'] = 'The invoice {} already exists'.format(invoice_number)
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer_id'] = self.kwargs['taxpayer_id']
        return context


class InvoiceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Invoice
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

    def post(self, request, *args, **kwargs):
        # Changing the status
        invoice = get_object_or_404(Invoice, id=self.kwargs['pk'])
        invoice.status = '2'
        invoice.save()

        # Creating a comment
        Comment.objects.create(
            user = request.user,
            invoice = invoice,
            message = '{} has changed the invoice'.format(
              request.user.email,
            )
        )

        # Change the invoices values
        self.object = self.get_object()
        return super(InvoiceUpdateView, self).post(request, *args, **kwargs)



    def user_has_permission(self):
        if not self.request.user.is_AP:
            # Only allow supplier to edit the invoice if status is 'CHANGES REQUEST'
            invoice = get_object_or_404(Invoice, id=self.kwargs['pk'])
            return invoice.status == INVOICE_STATUS_CHANGES_REQUEST

        return True

    def get_test_func(self):
        return self.user_has_permission

    def get_login_url(self):
        taxpayer_id = self.kwargs.get('taxpayer_id')
        if taxpayer_id:
            return reverse('supplier-invoice-list', kwargs={'taxpayer_id': taxpayer_id})
        else:
            return reverse('invoices-list')



class InvoiceHistory(ListView):
    model = Invoice
    template_name = 'invoices_app/history-list.html'

    def get_queryset(self):
        queryset = Invoice.history.filter(id=self.kwargs['pk'])
        return queryset


def invoice_history_changes(record):
    changes = []
    while record.next_record:
        next_record = record.next_record
        delta = next_record.diff_against(record)
        for change in delta.changes:
            changes.append({'field': change.field, 'old': change.old, 'new': change.new})
        record = next_record
    return changes

@is_ap_or_403()
def change_invoice_status(request, pk):
    status = request.POST.get('status')
    available_status_values = [value for (_, value) in INVOICE_STATUS]
    available_status_keys = [key for (key, _) in INVOICE_STATUS]

    if status not in available_status_keys and status not in available_status_values:
        return HttpResponseBadRequest()


    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.status =  status if status in available_status_keys else available_status_keys[available_status_values.index(status)]
    invoice.save()
    status_message = available_status_values[available_status_keys.index(invoice.status)]
    # Make a comment
    Comment.objects.create(
        invoice = invoice,
        user = request.user,
        message = '{} has changed the invoice status to {}'.format(
            request.user.email,
            status_message
        )
    )

    return redirect('invoices-list')


class InvoiceDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Invoice
    template_name = 'invoices_app/invoice_detail.html'
    login_url = '/'

    def test_func(self):
        taxpayer_id_in_url = self.kwargs['taxpayer_id']
        taxpayers_from_url = TaxPayer.objects.filter(pk=taxpayer_id_in_url)
        if not taxpayers_from_url:
            return False
        if self.request.user.is_AP:
            return True
        for taxpayer_from_url in taxpayers_from_url:
            company_from_taxpayer_in_url = taxpayer_from_url.company
            company_id = company_from_taxpayer_in_url.id

            # Is there a CompanyUserPermission that has that User and Company?
            companyuserpermission = \
                self.request.user.companyuserpermission_set.filter(
                    company=company_from_taxpayer_in_url
                )
            return True if companyuserpermission else False

        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice'] = get_object_or_404(Invoice, id=self.kwargs['pk'])
        father_taxpayer = get_object_or_404(TaxPayer, id=self.kwargs['taxpayer_id'])
        context['is_AP'] = self.request.user.is_AP
        context['taxpayer'] = father_taxpayer.get_taxpayer_child()
        context['address'] = Address.objects.get(taxpayer=father_taxpayer.get_taxpayer_child())
        context['INVOICE_STATUS_APPROVED'] = INVOICE_STATUS[0][0]
        context['INVOICE_STATUS_NEW'] = INVOICE_STATUS[1][0]
        context['INVOICE_STATUS_CHANGES_REQUEST'] = INVOICE_STATUS[2][0]
        context['INVOICE_STATUS_REJECTED'] = INVOICE_STATUS[3][0]
        context['INVOICE_STATUS_PAID'] = INVOICE_STATUS[4][0]
        context['comments'] = Comment.objects.filter(
            invoice=context['invoice']
        )
        return context
