from datetime import timedelta
from itertools import chain
import urllib

from django.contrib.auth.decorators import permission_required as permission_required_decorator
from django.contrib import messages
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.http import (
    HttpResponseBadRequest,
)
from django.shortcuts import (
    get_object_or_404,
    redirect
)
from django.urls import (
    reverse,
    reverse_lazy
)
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from bootstrap_datepicker_plus import DatePickerInput
from django_filters.views import FilterView
from pure_pagination.mixins import PaginationMixin

from invoices_app import (
    DEFAULT_NUMBER_PAGINATION,
    INVOICE_STATUS,
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_CHANGES_REQUEST,
    INVOICE_STATUS_NEW,
    INVOICE_STATUS_PAID,
    INVOICE_STATUS_REJECTED,
    ENGLISH_LANGUAGE_CODE,
    EXPORT_TO_XLS_FULL,
    INVOICE_DATE_FORMAT,
    INVOICE_MAX_SIZE_FILE,
)
from users_app import (
    CAN_EDIT_INVOICES_PERM,
    CAN_CHANGE_INVOICE_STATUS_PERM,
    CAN_CREATE_INVOICES_PERM,
    CAN_VIEW_ALL_INVOICES_PERM,
    CAN_VIEW_INVOICES_PERM,
    CAN_VIEW_INVOICES_HISTORY_PERM,
    CAN_VIEW_SUPPLIER_INVOICES_PERM,
)
from invoices_app.filters import InvoiceFilter
from invoices_app.forms import InvoiceForm
from invoices_app.models import (
    Invoice,
    Comment
)

from supplier_app import TAXPAYER_STATUS_APPROVED
from supplier_app.models import (
    TaxPayer,
    Address,
)

from users_app.decorators import (
    is_invoice_for_user,
)
from users_app.mixins import IsUserCompanyInvoice, TaxPayerPermissionMixin

from utils.file_validator import validate_file
from utils.history import invoice_history_comments
from utils.invoice_lookup import invoice_status_lookup
from utils.reports import (
    generate_xls,
    ExcelReportInputParams,
    generate_response_xls,
)
from utils.send_email import (
    build_mail_html,
    get_user_emails_by_tax_payer_id,
    send_email_notification
)


class InvoiceListView(PermissionRequiredMixin, PaginationMixin, FilterView):
    template_name = 'invoices_app/invoice-list.html'
    model = Invoice
    paginate_by = 10
    filterset_class = InvoiceFilter
    permission_required = CAN_VIEW_INVOICES_PERM

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_to_xls'] = urllib.parse.urlparse(self.request.get_raw_uri()).query
        context['is_AP'] = self.request.user.is_AP
        context['INVOICE_STATUS_APPROVED'] = invoice_status_lookup(INVOICE_STATUS_APPROVED)
        context['INVOICE_STATUS_NEW'] = invoice_status_lookup(INVOICE_STATUS_NEW)
        context['INVOICE_STATUS_CHANGES_REQUEST'] = invoice_status_lookup(INVOICE_STATUS_CHANGES_REQUEST)
        context['INVOICE_STATUS_REJECTED'] = invoice_status_lookup(INVOICE_STATUS_REJECTED)
        context['INVOICE_STATUS_PAID'] = invoice_status_lookup(INVOICE_STATUS_PAID)
        return context

    def get_queryset(self):
        user = self.request.user
        if user.has_perm(CAN_VIEW_ALL_INVOICES_PERM):
            queryset = Invoice.objects.filter().defer('invoice_file').order_by('id')
        else:
            queryset = Invoice.objects.filter(
                taxpayer__company__companyuserpermission__user=user
            ).defer('invoice_file')
        return queryset


class SupplierInvoiceListView(
    PermissionRequiredMixin,
    TaxPayerPermissionMixin,
    PaginationMixin,
    ListView
):

    template_name = 'supplier_app/invoice-list.html'
    model = Invoice
    paginate_by = 10
    fields = ['id', 'invoice_date', 'invoice_number', 'po_number', 'currency', 'total_amount', 'status']
    permission_required = CAN_VIEW_SUPPLIER_INVOICES_PERM

    def get_queryset(self):
        tax_payer = get_object_or_404(TaxPayer, id=self.kwargs['taxpayer_id'])
        queryset = Invoice.objects.filter(taxpayer=tax_payer.id).defer('invoice_file').order_by('id')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer'] = TaxPayer.objects.get(id=self.kwargs['taxpayer_id'])
        context['INVOICE_STATUS_APPROVED'] = invoice_status_lookup(INVOICE_STATUS_APPROVED)
        context['INVOICE_STATUS_NEW'] = invoice_status_lookup(INVOICE_STATUS_NEW)
        context['INVOICE_STATUS_CHANGES_REQUEST'] = invoice_status_lookup(INVOICE_STATUS_CHANGES_REQUEST)
        context['INVOICE_STATUS_REJECTED'] = invoice_status_lookup(INVOICE_STATUS_REJECTED)
        context['INVOICE_STATUS_PAID'] = invoice_status_lookup(INVOICE_STATUS_PAID)
        return context


class SupplierInvoiceCreateView(PermissionRequiredMixin, TaxPayerPermissionMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'supplier_app/invoices_form.html'
    permission_required = CAN_CREATE_INVOICES_PERM
    raise_exception = True

    def get_success_url(self):
        return reverse_lazy('supplier-invoice-list', kwargs={'taxpayer_id': self.kwargs['taxpayer_id']})

    def form_valid(self, form):
        form.instance.user = self.request.user
        taxpayer = get_object_or_404(TaxPayer, id=self.kwargs['taxpayer_id'])
        form.instance.taxpayer = taxpayer
        payment_term = taxpayer.get_taxpayer_child().payment_term
        form.instance.invoice_due_date = form.cleaned_data['invoice_date'] + timedelta(days=payment_term)
        invoice_number = form.cleaned_data['invoice_number']
        if taxpayer.taxpayer_state != TAXPAYER_STATUS_APPROVED:
            form.add_error(None, _('Taxpayer not approved yet'))
            return super().form_invalid(form)
        if Invoice.objects.filter(taxpayer=taxpayer.id, invoice_number=invoice_number).exists():
            form.errors['invoice_number'] = _('The invoice {} already exists').format(invoice_number)
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer_id'] = self.kwargs['taxpayer_id']
        context['is_AP'] = self.request.user.is_AP
        return context

    def get_form_class(self):
        form = self.form_class
        form.base_fields['invoice_date'].widget = DatePickerInput(
                options={
                    "format": str(INVOICE_DATE_FORMAT),
                    "locale": str(ENGLISH_LANGUAGE_CODE),
                },
                attrs={
                    'placeholder': _('Invoice Date'),
                }
            )
        return form


class InvoiceUpdateView(PermissionRequiredMixin, IsUserCompanyInvoice, UserPassesTestMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'supplier_app/invoices_form.html'
    redirect_field_name = None
    permission_required = CAN_EDIT_INVOICES_PERM

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        taxpayer_id = self.kwargs.get('taxpayer_id')
        if not taxpayer_id:
            taxpayer_id = Invoice.objects.get(id=int(self.kwargs['pk'])).taxpayer.id
        context['taxpayer_id'] = taxpayer_id
        context['is_AP'] = self.request.user.is_AP
        return context

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
        invoice.status = invoice_status_lookup(INVOICE_STATUS_NEW)
        invoice.save()

        if request.user.is_AP:
            subject = _('Eventbrite Invoice Edited')
            upper_text = _('Your Invoice # {} was edited by an administrator. \
                Please check your invoice').format(invoice.invoice_number)
            message = build_mail_html(
                invoice.taxpayer.business_name,
                upper_text,
                _('Thank you')
            )
            recipient_list = get_user_emails_by_tax_payer_id(invoice.taxpayer.id)
            send_email_notification.apply_async([subject, message, recipient_list])

        return super(UpdateView, self).post(request, *args, **kwargs)

    def user_has_permission(self):
        if not self.request.user.has_perm(CAN_CHANGE_INVOICE_STATUS_PERM):
            # Only allow supplier to edit the invoice if status is 'CHANGES REQUEST'
            invoice = get_object_or_404(Invoice, id=self.kwargs['pk'])
            return invoice.status == invoice_status_lookup(INVOICE_STATUS_CHANGES_REQUEST)

        return True

    def get_test_func(self):
        return self.user_has_permission

    def get_login_url(self):
        taxpayer_id = self.kwargs.get('taxpayer_id')
        if taxpayer_id:
            return reverse('supplier-invoice-list', kwargs={'taxpayer_id': taxpayer_id})
        else:
            return reverse('invoices-list')

    def get_form_class(self):
        form = self.form_class
        form.base_fields['invoice_date'].widget = DatePickerInput(
                options={
                    "format": str(INVOICE_DATE_FORMAT),
                    "locale": str(ENGLISH_LANGUAGE_CODE),
                },
                attrs={
                    'placeholder': _('Invoice Date'),
                }
            )
        return form


class InvoiceHistory(PermissionRequiredMixin, PaginationMixin, ListView):
    model = Invoice
    template_name = 'invoices_app/history-list.html'
    permission_required = CAN_VIEW_INVOICES_HISTORY_PERM
    paginate_by = DEFAULT_NUMBER_PAGINATION

    def get_queryset(self):
        queryset = Invoice.history.filter(id=self.kwargs['pk'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['INVOICE_STATUS_APPROVED'] = invoice_status_lookup(INVOICE_STATUS_APPROVED)
        context['INVOICE_STATUS_NEW'] = invoice_status_lookup(INVOICE_STATUS_NEW)
        context['INVOICE_STATUS_CHANGES_REQUEST'] = invoice_status_lookup(INVOICE_STATUS_CHANGES_REQUEST)
        context['INVOICE_STATUS_REJECTED'] = invoice_status_lookup(INVOICE_STATUS_REJECTED)
        context['INVOICE_STATUS_PAID'] = invoice_status_lookup(INVOICE_STATUS_PAID)
        return context


@permission_required_decorator(CAN_CHANGE_INVOICE_STATUS_PERM, raise_exception=True)
@is_invoice_for_user()
def change_invoice_status(request, pk):
    status = request.POST.get('status')
    available_status_keys = [key for (key, _) in INVOICE_STATUS]

    if status not in available_status_keys:
        return HttpResponseBadRequest()

    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.status = status
    invoice.save()

    # Email
    subject = _('Invoice {} changed status to {}').format(
            invoice.invoice_number,
            invoice.get_status_display(),
        )
    upper_text = _('Invoice {} changed status to {}').format(
                invoice.invoice_number,
                invoice.get_status_display(),
            )
    message = build_mail_html(
            invoice.taxpayer.business_name,
            upper_text,
            _('Thank you')
        )
    recipient_list = get_user_emails_by_tax_payer_id(invoice.taxpayer.id)
    send_email_notification.apply_async([subject, message, recipient_list])

    return redirect('invoices-list')


class InvoiceDetailView(PermissionRequiredMixin, IsUserCompanyInvoice, DetailView):
    model = Invoice
    template_name = 'invoices_app/invoice_detail.html'
    login_url = '/'
    permission_required = CAN_VIEW_INVOICES_PERM

    def get_comments(self, invoice):
        comments = Comment.objects.filter(
            invoice=invoice,
        ).order_by('-comment_date_received')

        history_comments = invoice_history_comments(invoice)

        result_list = sorted(
            chain(comments, history_comments),
            key=lambda instance: instance.comment_date_received,
            reverse=True,
        )
        return result_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = get_object_or_404(Invoice, id=self.kwargs['pk'])
        context['invoice'] = invoice
        father_taxpayer = get_object_or_404(TaxPayer, id=self.kwargs['taxpayer_id'])
        context['is_AP'] = self.request.user.is_AP
        context['taxpayer'] = father_taxpayer.get_taxpayer_child()
        context['address'] = Address.objects.get(taxpayer=father_taxpayer.get_taxpayer_child())
        context['INVOICE_STATUS_APPROVED'] = invoice_status_lookup(INVOICE_STATUS_APPROVED)
        context['INVOICE_STATUS_NEW'] = invoice_status_lookup(INVOICE_STATUS_NEW)
        context['INVOICE_STATUS_CHANGES_REQUEST'] = invoice_status_lookup(INVOICE_STATUS_CHANGES_REQUEST)
        context['INVOICE_STATUS_REJECTED'] = invoice_status_lookup(INVOICE_STATUS_REJECTED)
        context['INVOICE_STATUS_PAID'] = invoice_status_lookup(INVOICE_STATUS_PAID)
        context['comments'] = self.get_comments(invoice)
        return context


@is_invoice_for_user()
def post_a_comment(request, pk):
    # Check if message is empty
    if not request.POST.get('message'):
        return HttpResponseBadRequest()

    invoice = get_object_or_404(Invoice, pk=pk)

    if request.FILES:
        is_valid, msgs = validate_file(
            request.FILES['invoice_file'],
            INVOICE_MAX_SIZE_FILE
        )

        if not is_valid:
            for message in msgs:
                messages.error(request, message)

            return redirect(
                reverse(
                    'invoices-detail',
                    kwargs={
                        'taxpayer_id': invoice.taxpayer.id,
                        'pk': pk,
                    }
                )
            )

    Comment.objects.create(
        invoice=invoice,
        user=request.user,
        message=request.POST['message'],
        comment_file=request.FILES.get('invoice_file'),
    )

    if request.user.is_AP:
        subject = _('Eventbrite Invoice {} commented').format(invoice.invoice_number)
        upper_text = _('You have a new comment on Invoice # {}. Please check your invoice. COMMENT:{}').format(
            invoice.invoice_number,
            request.POST['message']
        )
        message = build_mail_html(
            invoice.taxpayer.business_name,
            upper_text,
            _('Thank you')
        )
        recipient_list = get_user_emails_by_tax_payer_id(invoice.taxpayer.id)
        send_email_notification.apply_async([subject, message, recipient_list])

    return redirect(
        reverse(
            'invoices-detail',
            kwargs={
                'taxpayer_id': invoice.taxpayer.id,
                'pk': pk,
            }
        )
    )


@permission_required_decorator(CAN_VIEW_INVOICES_PERM)
def export_to_xlsx_invoice(request):

    queryset = InvoiceFilter(request.GET, queryset=Invoice.objects.all()).qs
    params = ExcelReportInputParams(
        model=queryset,
        tab_name='Invoices',
        headers_attrs=EXPORT_TO_XLS_FULL,
    )
    xls_file = generate_xls(params)

    return generate_response_xls(xls_file, 'Invoices')
