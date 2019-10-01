from django.db import transaction
from django.views.generic import (
    TemplateView,
    ListView,
)
from django.views.generic.edit import (
    CreateView,
    FormView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import (
    reverse_lazy,
    reverse
)
from users_app.views import IsApUser
from supplier_app.models import (
    Company,
    CompanyUserPermission,
    PDFFile,
    TaxPayer,
    TaxPayerArgentina,
)
from supplier_app.forms import (
    AddressCreateForm,
    BankAccountCreateForm,
    PDFFileForm,
    TaxPayerCreateForm,
)

from . import TAXPAYER_STATUS_AP


class SupplierWithoutCompanyMixin(UserPassesTestMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            self.login_url = '/'
            return self.handle_no_permission()
        user_test_result = self.get_test_func()()
        if not user_test_result:
            self.login_url = reverse('company')
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        user_company = self.request.user.companyuserpermission_set.all()
        return len(user_company) > 0


class CompanySelectorView(LoginRequiredMixin, CreateView):
    model = CompanyUserPermission
    fields = ['company']
    template_name = 'supplier_app/company_selector.html'

    def get_success_url(self):
        return reverse('supplier-home')

    def form_invalid(self, form):
        return HttpResponseRedirect(reverse_lazy('company'), status=422)

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        form.instance.user = self.request.user
        form.save()
        return HttpResponseRedirect(self.get_success_url())


class CompanyCreatorView(LoginRequiredMixin, CreateView):
    model = Company
    fields = ['name', 'description']
    template_name = 'supplier_app/company_creation.html'

    def get_success_url(self):
        return reverse('supplier-home')

    @transaction.atomic
    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        company = form.save()
        companyuserpermission = CompanyUserPermission()
        companyuserpermission.user = self.request.user
        companyuserpermission.company = company
        companyuserpermission.save()
        return HttpResponseRedirect(self.get_success_url())


class SupplierHome(
    SupplierWithoutCompanyMixin,
    TemplateView
):
    model = TaxPayer
    template_name = 'supplier_app/supplier-home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayers'] = self.get_taxpayers()
        return context

    def get_taxpayers(self):
        user = self.request.user
        taxpayer_list = TaxPayer.objects.filter(company__companyuserpermission__user=user)
        taxpayer_child = [tax.get_taxpayer_child() for tax in taxpayer_list]
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


class CreateTaxPayerView(SupplierWithoutCompanyMixin, TemplateView, FormView):
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
        queryset = TaxPayerArgentina.objects.filter(taxpayer_state__in=TAXPAYER_STATUS_AP)
        return queryset


class SupplierDetailsView(LoginRequiredMixin, IsApUser, TemplateView):
    template_name = 'AP_app/ap-taxpayer-details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer'] = get_object_or_404(TaxPayer, pk=self.kwargs['taxpayer_id']).get_taxpayer_child()

        context['taxpayer_address'] = context['taxpayer'].address_set.get()
        context['taxpayer_bank_account'] = context['taxpayer'].bankaccount_set.get()

        return context
