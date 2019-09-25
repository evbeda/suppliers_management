from django.db import transaction
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.forms.models import ModelForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.http import HttpResponseRedirect
from django.urls import reverse

from invoices_app.models import (
    TaxPayerArgentina,
    Address,
    BankAccount,
    Invoice
)
from .models import PDFFile
from .forms import (
    InvoiceForm,
    PDFFileForm
)
from django.urls import (
    reverse_lazy
)


class InvoiceCreateView(CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'supplier_app/invoices_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super(InvoiceCreateView, self).form_valid(form)


class SupplierHome(LoginRequiredMixin, TemplateView):
    template_name = 'supplier_app/supplier-home.html'
    login_url = '/'


class CreatePDFFileView(CreateView):
    model = PDFFile
    form_class = PDFFileForm

    def get_success_url(self):
        return reverse_lazy('supplier-home')

    def form_valid(self, form):
        form.instance.file = self.request.FILES['pdf_file']
        self.object = form.save()
        return super(CreatePDFFileView, self).form_valid(form)


class PDFFileView(ListView):
    model = PDFFile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['files'] = PDFFile.objects.all()
        return context

class AddressCreateForm(ModelForm):
    prefix = 'address_form'

    class Meta:
        model = Address
        exclude = ['taxpayer']


class TaxPayerCreateForm(ModelForm):
    prefix = 'taxpayer_form'

    class Meta:
        model = TaxPayerArgentina
        exclude = ['taxpayer_state']


class BankAccountCreateForm(ModelForm):
    prefix = 'bankaccount_form'

    class Meta:
        model = BankAccount
        exclude = ['taxpayer']


class CreateTaxPayerView(TemplateView, FormView):
    template_name = 'supplier_app/taxpayer-creation.html'

    def get(self, request, *args, **kwargs):
        context = {
            'address_form': AddressCreateForm(),
            'taxpayer_form': TaxPayerCreateForm(),
            'bankaccount_form': BankAccountCreateForm(),
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        forms = {
            'taxpayer_form': TaxPayerCreateForm(self.request.POST),
            'address_form': AddressCreateForm(self.request.POST),
            'bankaccount_form': BankAccountCreateForm(self.request.POST),
        }
        if self.forms_are_valid(forms):
            return self.form_valid(forms)
        else:
            return self.form_invalid(forms)

    def forms_are_valid(self, forms):
        return all([form.is_valid() for form in forms.values()])

    def get_success_url(self):
        return reverse('supplier-home')

    def form_invalid(self, forms):
        return HttpResponseRedirect(self.get_success_url())

    @transaction.atomic
    def form_valid(self, forms):
        """
        If the form is valid, redirect to the supplied URL.
        """
        taxpayer = forms['taxpayer_form'].save()
        address = forms['address_form'].save(commit=False)
        address.taxpayer = taxpayer
        address.save()
        bankaccount = forms['bankaccount_form'].save(commit=False)
        bankaccount.taxpayer = taxpayer
        bankaccount.save()
        return HttpResponseRedirect(self.get_success_url())


class InvoiceListView(LoginRequiredMixin, ListView):
    template_name = 'supplier_app/invoice-list.html'
    model = Invoice

    def get_queryset(self):
        queryset = Invoice.objects.filter(taxpayer=self.kwargs['taxpayer_id'])
        return queryset
