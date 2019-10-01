from functools import reduce

from django.db import transaction
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.http import HttpResponseRedirect
from django.urls import (
    reverse_lazy,
    reverse
)

from users_app.views import IsApUser
from supplier_app.models import (
    PDFFile,
    TaxPayerArgentina,
    Company
)

from supplier_app.forms import (
    PDFFileForm,
    AddressCreateForm,
    BankAccountCreateForm,
    TaxPayerCreateForm
)


class SupplierHome(LoginRequiredMixin, TemplateView):
    model = TaxPayerArgentina
    template_name = 'supplier_app/supplier-home.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayers'] = self.get_taxpayers()
        return context

    def get_taxpayers(self):
        user = self.request.user
        companyuser = user.companyuserpermission_set.all()
        company = [c.company for c in companyuser]
        taxpayerlist = [c.taxpayer_set.all() for c in company]
        if not taxpayerlist:
            return []
        taxpayerlist = reduce(lambda a, b: a+b, taxpayerlist)
        taxpayer_child = [tax.get_taxpayer_child() for tax in taxpayerlist]
        return taxpayer_child


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


class CreateTaxPayerView(TemplateView, FormView):
    template_name = 'supplier_app/taxpayer-creation.html'

    def get(self, request, *args, **kwargs):
        context = {
            'address_form': AddressCreateForm(),
            'taxpayer_form': TaxPayerCreateForm(self.request.user),
            'bankaccount_form': BankAccountCreateForm(),
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        forms = {
            'taxpayer_form': TaxPayerCreateForm(request.user, self.request.POST),
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
        taxpayer = forms['taxpayer_form'].save(commit=False)
        company = Company.objects.filter(companyuserpermission__user=self.request.user)[0]
        taxpayer.company = company
        taxpayer.save()
        address = forms['address_form'].save(commit=False)
        address.taxpayer = taxpayer
        address.save()
        bankaccount = forms['bankaccount_form'].save(commit=False)
        bankaccount.taxpayer = taxpayer
        bankaccount.save()
        return HttpResponseRedirect(self.get_success_url())


class ApTaxpayers(LoginRequiredMixin, IsApUser, TemplateView):
    model = TaxPayerArgentina
    template_name = 'AP_app/ap-taxpayers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayers'] = self.get_queryset()
        return context

    def get_queryset(self):
        queryset = \
            TaxPayerArgentina.objects.filter(taxpayer_state='PENDING') | \
            TaxPayerArgentina.objects.filter(taxpayer_state='CHANGE REQUIRED')
        return queryset
