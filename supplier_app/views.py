from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db import DatabaseError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import (
    CreateView,
    FormView,
    UpdateView,
)
from django.views.generic.list import ListView
from django_filters.views import FilterView

from supplier_app.custom_messages import (
    COMPANY_ERROR_MESSAGE,
    EMAIL_ERROR_MESSAGE,
    EMAIL_SUCCESS_MESSAGE,
    JOIN_COMPANY_SUCCESS_MESSAGE,
    JOIN_COMPANY_ERROR_MESSAGE,
    TAXPAYER_CREATION_ERROR_MESSAGE,
    TAXPAYER_CREATION_SUCCESS_MESSAGE,
    TAXPAYER_FORM_INVALID_MESSAGE,
)
from supplier_app.filters import TaxPayerFilter
from supplier_app.forms import (
    AddressCreateForm,
    BankAccountCreateForm,
    BankAccountEditForm,
    TaxPayerCreateForm,
    TaxPayerEditForm
)
from supplier_app.models import (
    Address,
    BankAccount,
    Company,
    CompanyUniqueToken,
    CompanyUserPermission,
    TaxPayer,
    TaxPayerArgentina
)
from users_app.mixins import UserLoginPermissionRequiredMixin
from utils.exceptions import CouldNotSendEmailError
from utils.send_email import (
    company_invitation_notification,
    taxpayer_notification,
)


class CompanyCreatorView(UserLoginPermissionRequiredMixin, CreateView):
    model = Company
    fields = '__all__'
    template_name = 'AP_app/company_creation.html'
    success_url = reverse_lazy('ap-taxpayers')
    permission_required = (
        'users_app.can_create_company',
    )


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company


class SupplierHome(UserLoginPermissionRequiredMixin, TemplateView):
    model = TaxPayer
    template_name = 'supplier_app/supplier-home.html'
    permission_required = ('users_app.supplier_role', 'users_app.can_view_taxpayer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayers'] = self.get_taxpayers()
        context['user_has_company'] = self._user_has_company()
        return context

    def get_taxpayers(self):
        user = self.request.user
        taxpayer_list = TaxPayer.objects.filter(
            company__companyuserpermission__user=user
        )
        taxpayer_child = [tax.get_taxpayer_child() for tax in taxpayer_list]

        return taxpayer_child

    def _user_has_company(self):
        user = self.request.user
        if not user.companyuserpermission_set.all():
            messages.error(self.request, _(COMPANY_ERROR_MESSAGE))
            return False
        else:
            return True


class CreateTaxPayerView(UserLoginPermissionRequiredMixin, TemplateView, FormView):
    template_name = 'supplier_app/taxpayer-creation.html'
    permission_required = ('users_app.supplier_role', 'users_app.can_view_taxpayer', 'users_app.can_create_taxpayer')

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
        messages.error(
            self.request,
            _(TAXPAYER_FORM_INVALID_MESSAGE),
        )
        return HttpResponseRedirect(reverse('taxpayer-create'))

    @transaction.atomic
    def form_valid(self, forms):
        """
        If the form is valid, redirect to the supplied URL.
        """
        try:
            taxpayer = forms['taxpayer_form'].save(commit=False)
            company = Company.objects.get(companyuserpermission__user=self.request.user)
            taxpayer.company = company
            taxpayer.save()
            address = forms['address_form'].save(commit=False)
            address.taxpayer = taxpayer
            address.save()
            bankaccount = forms['bankaccount_form'].save(commit=False)
            bankaccount.taxpayer = taxpayer
            bankaccount.save()
            messages.success(
                self.request,
                _(TAXPAYER_CREATION_SUCCESS_MESSAGE)
            )
        except ObjectDoesNotExist:
            messages.error(
                self.request,
                _(TAXPAYER_CREATION_ERROR_MESSAGE)
            )
        finally:
            return HttpResponseRedirect(self.get_success_url())


class ApTaxpayers(UserLoginPermissionRequiredMixin, FilterView):
    model = TaxPayerArgentina
    template_name = 'AP_app/ap-taxpayers.html'
    filterset_class = TaxPayerFilter
    permission_required = (
        'users_app.can_view_all_taxpayers',
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        queryset = TaxPayer.objects.filter()
        return queryset


class SupplierDetailsView(UserLoginPermissionRequiredMixin, TemplateView):
    template_name = 'AP_app/ap-taxpayer-details.html'
    permission_required = (
        'users_app.can_view_taxpayer',
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer'] = get_object_or_404(TaxPayer, pk=self.kwargs['taxpayer_id']).get_taxpayer_child()
        context['taxpayer_address'] = context['taxpayer'].address_set.get()
        context['taxpayer_bank_account'] = context['taxpayer'].bankaccount_set.get()
        context['workday_id_is_setted'] = context['taxpayer'].has_workday_id()
        context['is_AP'] = self.request.user.is_AP
        return context


class EditTaxpayerView(UserLoginPermissionRequiredMixin, UpdateView):
    template_name = 'AP_app/edit-taxpayer-information.html'
    model = TaxPayerArgentina
    form_class = TaxPayerEditForm
    pk_url_kwarg = "taxpayer_id"
    permission_required = (
        'users_app.can_edit_taxpayer',
    )

    def get_success_url(self, **kwargs):
        taxpayer_id = self.kwargs['taxpayer_id']
        return reverse('supplier-details', kwargs={'taxpayer_id': taxpayer_id})


class EditAddressView(UserLoginPermissionRequiredMixin, UpdateView):
    template_name = 'AP_app/edit-address-information.html'
    model = Address
    form_class = AddressCreateForm
    pk_url_kwarg = "address_id"
    permission_required = (
        'users_app.can_edit_taxpayer',
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer_id'] = Address.objects.get(pk=self.kwargs['address_id']).taxpayer.id
        return context

    def get_success_url(self, **kwargs):
        taxpayer_id = Address.objects.get(pk=self.kwargs['address_id']).taxpayer.id
        return reverse('supplier-details', kwargs={'taxpayer_id': taxpayer_id})


class EditBankAccountView(UserLoginPermissionRequiredMixin, UpdateView):
    template_name = 'AP_app/edit-bank-account-information.html'
    model = BankAccount
    form_class = BankAccountEditForm
    pk_url_kwarg = "bank_id"
    permission_required = (
        'users_app.can_edit_taxpayer',
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer_id'] = BankAccount.objects.get(pk=self.kwargs['bank_id']).taxpayer.id
        return context

    def get_success_url(self, **kwargs):
        taxpayer_id = BankAccount.objects.get(pk=self.kwargs['bank_id']).taxpayer.id
        return reverse('supplier-details', kwargs={'taxpayer_id': taxpayer_id})


@permission_required('users_app.can_approve', raise_exception=True)
def approve_taxpayer(self, taxpayer_id, request=None):
    taxpayer = TaxPayer.objects.get(pk=taxpayer_id)
    taxpayer.approve_taxpayer()
    taxpayer.save()
    taxpayer_notification(taxpayer, 'taxpayer_approval')
    return redirect('ap-taxpayers')


@transaction.atomic
def company_invite(request):
    try:
        email = [request.POST['email']]
        company_id = request.POST['company_id']
        company = Company.objects.get(pk=company_id)
        company_unique_token = CompanyUniqueToken(company=company)
        company_unique_token.assing_company_token
        company_unique_token.save()
        token = company_unique_token.token
        company_invitation_notification(company, token, email)
        messages.success(request, _(EMAIL_SUCCESS_MESSAGE))
    except CouldNotSendEmailError:
        messages.error(request, _(EMAIL_ERROR_MESSAGE))
    finally:
        return redirect('company-list')


@permission_required('users_app.supplier_role', raise_exception=True)
def company_join(request, *args, **kwargs):
    company_unique_token = _get_company_unique_token_from_token(kwargs['token'])
    if _token_is_valid(company_unique_token):
        try:
            user = request.user
            company = company_unique_token.company
            CompanyUserPermission.objects.create(user=user, company=company)
            company_unique_token.delete()
            messages.success(request, JOIN_COMPANY_SUCCESS_MESSAGE)
        except DatabaseError:
            messages.error(request, JOIN_COMPANY_ERROR_MESSAGE)
        finally:
            return redirect('supplier-home')
    return HttpResponseRedirect(Http404)


def _token_is_valid(company_unique_token):
    return company_unique_token and not company_unique_token.is_token_expired


def _get_company_unique_token_from_token(token):
    return get_object_or_404(CompanyUniqueToken, token=token)


@permission_required('users_app.can_approve', raise_exception=True)
def deny_taxpayer(self, taxpayer_id, request=None):
    taxpayer = TaxPayer.objects.get(pk=taxpayer_id)
    taxpayer.deny_taxpayer()
    taxpayer.save()
    taxpayer_notification(taxpayer, 'taxpayer_denial')
    return redirect('ap-taxpayers')
