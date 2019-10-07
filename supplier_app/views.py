from django.db import transaction
from django.views.generic import (
    TemplateView,
)
from django.views.generic.edit import (
    CreateView,
    FormView,
    UpdateView
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
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
    TaxPayer,
    TaxPayerArgentina,
    BankAccount,
)
from supplier_app.forms import (
    AddressCreateForm,
    BankAccountCreateForm,
    BankAccountEditForm,
    TaxPayerCreateForm,
    TaxPayerEditForm,
)

from supplier_app import (
    get_taxpayer_status_pending_and_change_required
)


class CompanyCreatorView(LoginRequiredMixin, IsApUser, CreateView):
    model = Company
    fields = '__all__'
    template_name = 'AP_app/company_creation.html'
    success_url = reverse_lazy('ap-taxpayers')


class SupplierHome(
    LoginRequiredMixin,
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
        taxpayer_list = TaxPayer.objects.filter(
            company__companyuserpermission__user=user
        )
        taxpayer_child = [tax.get_taxpayer_child() for tax in taxpayer_list]
        return taxpayer_child


class CreateTaxPayerView(LoginRequiredMixin, TemplateView, FormView):
    template_name = 'supplier_app/taxpayer-creation.html'

    def get_context_data(self, **kwargs):
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
        queryset = TaxPayerArgentina.objects.filter(
            taxpayer_state__in=get_taxpayer_status_pending_and_change_required()
        )
        return queryset


class SupplierDetailsView(LoginRequiredMixin, IsApUser, TemplateView):
    template_name = 'AP_app/ap-taxpayer-details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer'] = get_object_or_404(TaxPayer, pk=self.kwargs['taxpayer_id']).get_taxpayer_child()
        context['taxpayer_address'] = context['taxpayer'].address_set.get()
        context['taxpayer_bank_account'] = context['taxpayer'].bankaccount_set.get()
        context['workday_id_is_setted'] = context['taxpayer'].has_workday_id()

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
        taxpayer_db.payment_term = taxpayer_form.payment_term
        taxpayer_db.taxpayer_comments = taxpayer_form.taxpayer_comments

        taxpayer_db.save()

        return HttpResponseRedirect(self.get_success_url())


class EditAddressView(UpdateView):
    template_name = 'AP_app/edit-address-information.html'
    model = Address
    form_class = AddressCreateForm
    pk_url_kwarg = "address_id"

    def get_success_url(self, **kwargs):
        taxpayer_id = Address.objects.get(pk=self.kwargs['address_id']).taxpayer.id
        return reverse('supplier-details', kwargs={'taxpayer_id': taxpayer_id})


class EditBankAccountView(UpdateView):
    template_name = 'AP_app/edit-bank-account-information.html'
    model = BankAccount
    form_class = BankAccountEditForm
    pk_url_kwarg = "bank_id"

    def get_success_url(self, **kwargs):
        taxpayer_id = BankAccount.objects.get(pk=self.kwargs['bank_id']).taxpayer.id
        return reverse('supplier-details', kwargs={'taxpayer_id': taxpayer_id})


def approve_taxpayer(self, taxpayer_id, request=None):
    taxpayer = TaxPayer.objects.get(pk=taxpayer_id)
    taxpayer.approve_taxpayer()
    taxpayer.save()
    return redirect('ap-taxpayers')


def deny_taxpayer(self, taxpayer_id, request=None):
    taxpayer = TaxPayer.objects.get(pk=taxpayer_id)
    taxpayer.deny_taxpayer()
    taxpayer.save()
    return redirect('ap-taxpayers')
