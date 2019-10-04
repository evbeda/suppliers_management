from django.db import transaction
from django.views.generic import (
    TemplateView,
)
from django.views.generic.edit import (
    CreateView,
    FormView,
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import (
    reverse_lazy,
    reverse,
)
from users_app.views import IsApUser
from supplier_app.models import (
    Address,
    Company,
    CompanyUserPermission,
    TaxPayer,
    TaxPayerArgentina,
    BankAccount,
)
from supplier_app.forms import (
    AddressCreateForm,
    BankAccountCreateForm,
    TaxPayerCreateForm,
    TaxPayerEditForm,
)

from . import TAXPAYER_STATUS_AP, TAXPAYER_STATUS


class SupplierWithoutCompanyMixin(UserPassesTestMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            self.login_url = '/'
            return self.handle_no_permission()
        user_test_result = self.get_test_func()()
        if not user_test_result:
            self.login_url = reverse('company-selector')
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
        return HttpResponseRedirect(reverse_lazy('company-selector'), status=422)

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


class CreateTaxPayerView(SupplierWithoutCompanyMixin, TemplateView, FormView):
    template_name = 'supplier_app/taxpayer-creation.html'

    def get_context_data(self, **kwargs):
        """
        Insert the form into the context dict.
        """
        kwargs.update({
            'address_form': AddressCreateForm(),
            'taxpayer_form': TaxPayerCreateForm(),
            'bank_account_form': BankAccountCreateForm(),
        })
        return kwargs

    def post(self, request, *args, **kwargs):
        forms = {
            'taxpayer_form': TaxPayerCreateForm(
                data=request.POST,
                files=request.FILES),
            'address_form': AddressCreateForm(data=request.POST),
            'bankaccount_form': BankAccountCreateForm(
                data=request.POST,
                files=request.FILES),
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


class EditTaxpayerView(FormView):
    template_name = 'AP_app/edit-taxpayer-information.html'

    def get(self, request, *args, **kwargs):
        taxpayer = get_object_or_404(TaxPayer, pk=self.kwargs['taxpayer_id']).get_taxpayer_child()
        edit_form = TaxPayerEditForm(instance=taxpayer)
        context = {
            'taxpayer_form': edit_form
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):

        taxpayer_form = TaxPayerEditForm(data=request.POST, files=request.FILES)

        if taxpayer_form.is_valid():
            return self.form_valid(taxpayer_form)
        else:
            return self.form_invalid(taxpayer_form)

    def get_success_url(self, **kwargs):
        taxpayer_id = self.kwargs['taxpayer_id']
        return reverse('supplier-details', kwargs={'taxpayer_id': taxpayer_id})

    def form_invalid(self, forms):
        return HttpResponseRedirect(self.get_success_url())

    @transaction.atomic
    def form_valid(self, form):

        taxpayer_form = form.save(commit=False)

        taxpayer_db = get_object_or_404(TaxPayer, pk=self.kwargs['taxpayer_id']).get_taxpayer_child()

        taxpayer_db.workday_id = taxpayer_form.workday_id
        taxpayer_db.business_name = taxpayer_form.business_name
        taxpayer_db.cuit = taxpayer_form.cuit
        taxpayer_db.payment_type = taxpayer_form.payment_type
        taxpayer_db.comments = taxpayer_form.comments

        taxpayer_db.save()

        return HttpResponseRedirect(self.get_success_url())


class EditAddressView(FormView):
    template_name = 'AP_app/edit-address-information.html'

    def get(self, request, *args, **kwargs):
        taxpayer_id = self.kwargs['taxpayer_id']
        taxpayer_address = get_object_or_404(Address, taxpayer__id=taxpayer_id)
        edit_form = AddressCreateForm(instance=taxpayer_address)
        context = {
            'address_form': edit_form
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):

        taxpayer_form = AddressCreateForm(self.request.POST)

        if taxpayer_form.is_valid():
            return self.form_valid(taxpayer_form)
        else:
            return self.form_invalid(taxpayer_form)

    def get_success_url(self, **kwargs):
        taxpayer_id = self.kwargs['taxpayer_id']
        return reverse('supplier-details', kwargs={'taxpayer_id': taxpayer_id})

    def form_invalid(self, forms):
        return HttpResponseRedirect(self.get_success_url())

    @transaction.atomic
    def form_valid(self, form):
        taxpayer_id = self.kwargs['taxpayer_id']
        taxpayer_form = form.save(commit=False)

        taxpayer_db = get_object_or_404(Address, taxpayer__id=taxpayer_id)

        taxpayer_db.street = taxpayer_form.street
        taxpayer_db.number = taxpayer_form.number
        taxpayer_db.zip_code = taxpayer_form.zip_code
        taxpayer_db.city = taxpayer_form.city
        taxpayer_db.state = taxpayer_form.state
        taxpayer_db.country = taxpayer_form.country

        taxpayer_db.save()

        return HttpResponseRedirect(self.get_success_url())


class EditBankAccountView(FormView):
    template_name = 'AP_app/edit-bank-account-information.html'

    def get(self, request, *args, **kwargs):
        taxpayer_id = self.kwargs['taxpayer_id']
        taxpayer_bank_account = get_object_or_404(BankAccount, taxpayer__id=taxpayer_id)
        edit_form = BankAccountCreateForm(instance=taxpayer_bank_account)
        context = {
            'bank_account_form': edit_form
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):

        taxpayer_form = BankAccountCreateForm(data=request.POST, files=request.FILES)

        if taxpayer_form.is_valid():
            return self.form_valid(taxpayer_form)
        else:
            return self.form_invalid(taxpayer_form)

    def get_success_url(self, **kwargs):
        taxpayer_id = self.kwargs['taxpayer_id']
        return reverse('supplier-details', kwargs={'taxpayer_id': taxpayer_id})

    def form_invalid(self, forms):
        return HttpResponseRedirect(self.get_success_url())

    @transaction.atomic
    def form_valid(self, form):
        taxpayer_id = self.kwargs['taxpayer_id']
        taxpayer_form = form.save(commit=False)

        taxpayer_db = get_object_or_404(BankAccount, taxpayer__id=taxpayer_id)

        taxpayer_db.bank_name = taxpayer_form.bank_name
        taxpayer_db.bank_code = taxpayer_form.bank_code
        taxpayer_db.bank_account_number = taxpayer_form.bank_account_number

        taxpayer_db.save()

        return HttpResponseRedirect(self.get_success_url())


def approve_taxpayer(request, taxpayer_id):
    taxpayer = TaxPayer.objects.get(pk=taxpayer_id)
    taxpayer.taxpayer_state = TAXPAYER_STATUS[0][0]
    taxpayer.save()
    return redirect('ap-taxpayers')


def refuse_taxpayer(request, taxpayer_id):
    taxpayer = TaxPayer.objects.get(pk=taxpayer_id)
    taxpayer.taxpayer_state = TAXPAYER_STATUS[3][0]
    taxpayer.save()
    return redirect('ap-taxpayers')
