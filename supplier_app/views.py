from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db import DatabaseError
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, View
from django.views.generic.edit import (
    CreateView,
    FormView,
    UpdateView,
)
from datetime import datetime
from django.views.generic.list import ListView
from django.utils import translation
from django_filters.views import FilterView

from invoices_app import EXPORT_TO_XLS_FULL, EXPORT_TO_XLS_TAXPAYER
from supplier_app import DATE_FORMAT
from supplier_app.change_status_strategy import (
    run_strategy_taxpayer_status,
)
from supplier_app.constants.custom_messages import (
    COMPANY_ERROR_MESSAGE,
    EMAIL_ERROR_MESSAGE,
    EMAIL_SUCCESS_MESSAGE,
    JOIN_COMPANY_SUCCESS_MESSAGE,
    JOIN_COMPANY_ERROR_MESSAGE,
    TAXPAYER_COMMENT_EMPTY,
    TAXPAYER_CREATION_ERROR_MESSAGE,
    TAXPAYER_CREATION_SUCCESS_MESSAGE,
    TAXPAYER_FORM_INVALID_MESSAGE,
    TAXPAYER_NOT_EXISTS_MESSAGE,
    TAXPAYER_WITHOUT_WORKDAY_ID_MESSAGE,
    TAXPAYER_WORKDAY_UNIQUE_ERROR,
    THANKS,
    COMPANY_ALREADY_EXIST,
)
from supplier_app.constants.taxpayer_status import (
    TAXPAYER_STATUS_APPROVED,
    TAXPAYER_STATUS_CHANGE_REQUIRED,
    TAXPAYER_STATUS_DENIED,
    TAXPAYER_STATUS_IN_PROGRESS,
    TAXPAYER_STATUS_CHANGES_PENDING)
from supplier_app.filters import TaxPayerFilter
from supplier_app.forms import (
    AddressCreateForm,
    BankAccountCreateForm,
    BankAccountEditForm,
    TaxPayerCreateForm,
    TaxPayerEditForm,
    ContactInformationCreateForm,
)
from supplier_app.exceptions.taxpayer_exceptions import (
    NoWorkdayIDException,
    TaxpayerUniqueWorkdayId,
)

from supplier_app.models import (
    Address,
    BankAccount,
    Company,
    CompanyUniqueToken,
    CompanyUserPermission,
    EBEntity,
    TaxPayer,
    TaxPayerArgentina,
    TaxpayerComment,
    TaxPayerEBEntity,
    ContactInformation,
    InvitingBuyer,
    EBEntityCompany
)
from users_app.mixins import (
    TaxPayerPermissionMixin,
    UserLoginPermissionRequiredMixin,
)
from users_app import (
    CAN_CREATE_COMPANY_PERM,
    CAN_CREATE_TAXPAYER_PERM,
    CAN_EDIT_TAXPAYER_ADDRESS_PERM,
    CAN_EDIT_TAXPAYER_BANK_ACCOUNT_PERM,
    CAN_EDIT_TAXPAYER_PERM,
    CAN_VIEW_ALL_TAXPAYERS_PERM,
    CAN_VIEW_TAXPAYER_HISTORY_PERM,
    CAN_VIEW_TAXPAYER_PERM,
    COMPANY_USER_CAN_APPROVE_PERM,
    SUPPLIER_ROLE_PERM,
)
from users_app.models import User
from utils import reports
from utils.exceptions import CouldNotSendEmailError
from utils.reports import ExcelReportInputParams, generate_xls, generate_response_xls
from utils.send_email import company_invitation_notification
from utils.htmltopdf import render_to_pdf
from django.contrib.auth.decorators import permission_required as permission_required_decorator


class CompanyCreatorView(UserLoginPermissionRequiredMixin, CreateView):
    model = Company
    fields = '__all__'
    template_name = 'supplier_app/AP/company_creation.html'
    permission_required = (
        CAN_CREATE_COMPANY_PERM,
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['eb_entities'] = EBEntity.objects.all()
        return context

    def form_valid(self, form):
        lowercase_company_names = [name[0].lower() for name in Company.objects.values_list('name')]
        if form.data['name'].lower() in lowercase_company_names or User.objects.filter(email=self.request.POST['email']):
            return HttpResponseRedirect(self.get_failure_url())
        company = self.save_company(form)
        InvitingBuyer.objects.create(company=company, inviting_buyer=self.request.user)
        EBEntityCompany.objects.create(company=company, eb_entity=EBEntity.objects.get(pk=form.data['eb_entity']))
        company_invite(self.request, company)
        return HttpResponseRedirect(self.get_success_url())

    def save_company(self, forms):
        company = forms.save(commit=False)
        company.save()
        return company

    def get_success_url(self):
        if self.request.user.is_AP:
            return reverse('company-list-deprecated')
        else:
            return reverse('company-list')

    def get_failure_url(self):
        messages.error(
            self.request,
            COMPANY_ALREADY_EXIST,
        )
        return reverse('company-create')


class CompanyManage(LoginRequiredMixin, ListView):
    model = User
    template_name = 'supplier_app/Supplier/company_manage.html'

    def get_queryset(self):
        # TODO: First resolve the bug that does not allow duplicate inserts in this table CompanyUserPermission
        #  to use the next line
        # company = CompanyUserPermission.objects.get(user_id=self.request.user.id)
        if self.request.user.is_AP:
            return User.objects.filter(groups=1)
        else:
            company = CompanyUserPermission.objects.filter(user_id=self.request.user.id).first()
            return User.objects.filter(companyuserpermission__company=company.company)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for u in self.object_list:
            queryset = CompanyUserPermission.objects.filter(user=u).first()
            if queryset:
                u.company = queryset.company.name
        return context


def change_user_status(request, pk):
    new_status = request.POST.get('active')
    user = get_object_or_404(User, id=pk)
    if new_status == 'activate':
        user.is_active = True
    elif new_status == 'deactivate':
        user.is_active = False
    user.save()
    return redirect('company-manage')


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'supplier_app/AP/company_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_AP'] = self.request.user.is_AP
        context['all_companies'] = Company.objects.values('name')
        return context

    def get_queryset(self):
        company_name = self.request.GET.get('company')
        if company_name:
            queryset = Company.objects.filter(name__icontains=company_name)
        else:
            queryset = Company.objects.all()
        return queryset


class SupplierHome(UserLoginPermissionRequiredMixin, TemplateView):
    model = TaxPayer
    template_name = 'supplier_app/supplier-home.html'
    permission_required = (SUPPLIER_ROLE_PERM, CAN_VIEW_TAXPAYER_PERM)

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
            messages.error(self.request, COMPANY_ERROR_MESSAGE)
            return False
        else:
            return True


class CreateTaxPayerView(UserLoginPermissionRequiredMixin, TemplateView, FormView):
    template_name = 'supplier_app/Supplier/taxpayer-creation.html'
    permission_required = (SUPPLIER_ROLE_PERM, CAN_VIEW_TAXPAYER_PERM, CAN_CREATE_TAXPAYER_PERM)

    def get(self, request, *args, **kwargs):
        kwargs['forms'] = {
            'address_form': AddressCreateForm(),
            'taxpayer_form': TaxPayerCreateForm(),
            'bank_account_form': BankAccountCreateForm(),
            'contact_form': ContactInformationCreateForm(),
        }
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        forms = self._create_forms_from_request(request)
        if self.forms_are_valid(forms):
            return self.form_valid(forms)
        else:
            return self.form_invalid(forms)

    def get_context_data(self, **kwargs):
        if 'forms' in kwargs:
            kwargs.update(**kwargs['forms'])
        return kwargs

    def _create_forms_from_request(self, request):
        return {
            'taxpayer_form': TaxPayerCreateForm(
                data=request.POST,
                files=request.FILES),
            'address_form': AddressCreateForm(data=request.POST),
            'bank_account_form': BankAccountCreateForm(
                data=request.POST,
                files=request.FILES),
            'contact_form': ContactInformationCreateForm(data=request.POST),
        }

    def get_success_url(self):
        return reverse('supplier-home')

    def forms_are_valid(self, forms):
        return all([form.is_valid() for form in forms.values()])

    def form_invalid(self, forms):
        new_forms = {}
        messages.error(
            self.request,
            TAXPAYER_FORM_INVALID_MESSAGE,
        )
        for k, v in forms.items():
            new_forms[k] = v

        kwargs = {}
        kwargs['forms'] = new_forms

        return self.render_to_response(
            self.get_context_data(**kwargs)
        )

    @transaction.atomic
    def form_valid(self, forms):
        """
        If the form is valid, redirect to the supplied URL.
        """
        try:
            taxpayer = self.save_taxpayer(forms)
            self.save_contact(forms, taxpayer, self.save_address(forms, taxpayer))
            self.save_bankaccount(forms, taxpayer)
            messages.success(
                self.request,
                TAXPAYER_CREATION_SUCCESS_MESSAGE,
            )
            messages.success(
                self.request,
                THANKS,
            )
        except ObjectDoesNotExist:
            messages.error(
                self.request,
                TAXPAYER_CREATION_ERROR_MESSAGE
            )
        finally:
            return HttpResponseRedirect(self.get_success_url())

    def save_taxpayer(self, forms):
        taxpayer = forms['taxpayer_form'].save(commit=False)
        company = Company.objects.get(companyuserpermission__user=self.request.user)
        taxpayer.company = company
        
        taxpayer.save()
        eb_entities = forms['taxpayer_form'].cleaned_data['eb_entities']
        eb_entity = EBEntity.objects.get(pk=eb_entities)
        TaxPayerEBEntity.objects.create(
            eb_entity=eb_entity,
            taxpayer=taxpayer
        )
        return taxpayer

    def save_address(self, forms, taxpayer):
        address = forms['address_form'].save(commit=False)
        address.taxpayer = taxpayer
        address.save()
        return address

    def save_contact(self, forms, taxpayer, address):
        contact = forms['contact_form'].save(commit=False)
        contact.taxpayer = taxpayer
        contact.address = address
        contact.save()

    def save_bankaccount(self, forms, taxpayer):
        bankaccount = forms['bank_account_form'].save(commit=False)
        bankaccount.taxpayer = taxpayer
        bankaccount.save()


class ApTaxpayers(UserLoginPermissionRequiredMixin, FilterView):
    model = TaxPayerArgentina
    template_name = 'supplier_app/ap-taxpayers.html'
    filterset_class = TaxPayerFilter
    permission_required = (
        CAN_VIEW_ALL_TAXPAYERS_PERM,
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        queryset = TaxPayer.objects.filter()
        return queryset


class SupplierDetailsView(UserLoginPermissionRequiredMixin, TaxPayerPermissionMixin, TemplateView):
    template_name = 'supplier_app/taxpayer-details.html'
    permission_required = (CAN_VIEW_TAXPAYER_PERM)

    def handle_no_permission(self):
        return HttpResponseRedirect(Http404)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        taxpayer = get_object_or_404(TaxPayer, pk=self.kwargs['taxpayer_id']).get_taxpayer_child()
        if self.request.user.is_AP:
            if taxpayer.new_comment_from_supplier is True:
                taxpayer.new_comment_from_supplier = False
                taxpayer.save()
        if self.request.user.is_supplier:
            if taxpayer.new_comment_from_ap is True:
                taxpayer.new_comment_from_ap = False
                taxpayer.save()
        context['taxpayer'] = taxpayer
        context['taxpayer_address'] = context['taxpayer'].address_set.get()
        context['taxpayer_contact'] = context['taxpayer'].contactinformation_set.get()
        context['taxpayer_bank_account'] = context['taxpayer'].bankaccount_set.get()
        context['workday_id_is_setted'] = context['taxpayer'].has_workday_id()
        context['comments'] = context['taxpayer'].taxpayercomment_set.all()
        context['approve'] = TAXPAYER_STATUS_APPROVED
        context['change_required'] = TAXPAYER_STATUS_CHANGE_REQUIRED
        context['deny'] = TAXPAYER_STATUS_DENIED
        context['in_progress'] = TAXPAYER_STATUS_IN_PROGRESS
        context['make_comment'] = 'make comment'
        context['is_AP'] = self.request.user.is_AP
        return context


class EditTaxpayerView(UserLoginPermissionRequiredMixin, TaxPayerPermissionMixin, UpdateView):
    template_name = 'supplier_app/edit-taxpayer-information.html'
    model = TaxPayerArgentina
    form_class = TaxPayerEditForm
    pk_url_kwarg = "taxpayer_id"
    permission_required = (
        CAN_EDIT_TAXPAYER_PERM,
    )

    def post(self, request, **kwargs):
        self.object = self.get_object()

        eb_entities = EBEntity.objects.filter(
            pk__in=request.POST.getlist('eb_entities')
        )
        self.object.set_current_eb_entities(eb_entities)
        form = self.get_form()

        if form.is_valid():
            if request.user.is_supplier:
                except_field = ['csrfmiddlewaretoken', 'eb_entities']
                taxpayer_to_compare = TaxPayerArgentina.objects.get(pk=kwargs['taxpayer_id'])
                text_to_coment = reports.get_field_changes(form, except_field, taxpayer_to_compare)
                TaxpayerComment.objects.create(user=request.user, message=text_to_coment, taxpayer=taxpayer_to_compare)
                form.instance.set_changes_pending_taxpayer()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer_id'] = self.kwargs['taxpayer_id']
        taxpayer = TaxPayerArgentina.objects.get(pk=context['taxpayer_id'])
        form = context['form']
        
        form.fields['afip_registration_file'].initial = taxpayer.afip_registration_file
        form.fields['witholding_taxes_file'].initial = taxpayer.witholding_taxes_file
        # Todo: migrate relation to OneToOne
        form.fields['eb_entities'].initial = taxpayer.eb_entities.pop().id
        return context

    def handle_no_permission(self):
        return HttpResponseRedirect(Http404)

    def get_success_url(self, **kwargs):
        taxpayer_id = self.kwargs['taxpayer_id']
        return reverse('supplier-details', kwargs={'taxpayer_id': taxpayer_id})


class EditAddressView(UserLoginPermissionRequiredMixin, TaxPayerPermissionMixin, UpdateView):
    template_name = 'supplier_app/edit-address-information.html'
    model = Address
    form_class = AddressCreateForm
    pk_url_kwarg = "address_id"
    permission_required = (
        CAN_EDIT_TAXPAYER_PERM,
        CAN_EDIT_TAXPAYER_ADDRESS_PERM,
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        taxpayer = get_object_or_404(TaxPayer, id=self.kwargs['taxpayer_id'])
        context['taxpayer_id'] = taxpayer.id
        get_object_or_404(Address, pk=self.kwargs['address_id'], taxpayer=taxpayer)
        return context

    def handle_no_permission(self):
        return HttpResponseRedirect(Http404)

    def get_success_url(self, **kwargs):
        taxpayer_id = Address.objects.get(pk=self.kwargs['address_id']).taxpayer.id
        return reverse('supplier-details', kwargs={'taxpayer_id': taxpayer_id})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid() and request.user.is_supplier:
            taxpayer_to_compare = TaxPayerArgentina.objects.get(pk=kwargs['taxpayer_id'])
            model_to_compare = Address.objects.get(taxpayer_id=kwargs['taxpayer_id'])
            text_to_coment = reports.get_field_changes(form, [], model_to_compare)
            TaxpayerComment.objects.create(user=request.user, message=text_to_coment, taxpayer=taxpayer_to_compare)
            taxpayer = TaxPayer.objects.get(pk=self.kwargs['taxpayer_id'])
            taxpayer.set_changes_pending_taxpayer()
            taxpayer.save()
        return super().post(request, *args, **kwargs)


class EditContactInformationView(UserLoginPermissionRequiredMixin, TaxPayerPermissionMixin, UpdateView):
    template_name = 'supplier_app/edit-contact-information.html'
    model = ContactInformation
    form_class = ContactInformationCreateForm
    pk_url_kwarg = "contact_id"
    permission_required = (
        CAN_EDIT_TAXPAYER_PERM,
        CAN_EDIT_TAXPAYER_ADDRESS_PERM,
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        taxpayer = get_object_or_404(TaxPayer, id=self.kwargs['taxpayer_id'])
        context['taxpayer_id'] = taxpayer.id
        get_object_or_404(ContactInformation, pk=self.kwargs['contact_id'], taxpayer=taxpayer)
        return context

    def handle_no_permission(self):
        return HttpResponseRedirect(Http404)

    def get_success_url(self, **kwargs):
        taxpayer_id = ContactInformation.objects.get(pk=self.kwargs['contact_id']).taxpayer.id
        return reverse('supplier-details', kwargs={'taxpayer_id': taxpayer_id})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid() and request.user.is_supplier:
            taxpayer_to_compare = TaxPayerArgentina.objects.get(pk=kwargs['taxpayer_id'])
            model_to_compare = ContactInformation.objects.get(taxpayer_id=kwargs['taxpayer_id'])
            text_to_coment = reports.get_field_changes(form, [], model_to_compare)
            TaxpayerComment.objects.create(user=request.user, message=text_to_coment, taxpayer=taxpayer_to_compare)
            taxpayer = TaxPayer.objects.get(pk=self.kwargs['taxpayer_id'])
            taxpayer.set_changes_pending_taxpayer()
            taxpayer.save()
        return super().post(request, *args, **kwargs)


class EditBankAccountView(UserLoginPermissionRequiredMixin, TaxPayerPermissionMixin, UpdateView):
    template_name = 'supplier_app/edit-bank-account-information.html'
    model = BankAccount
    form_class = BankAccountEditForm
    pk_url_kwarg = "bank_id"
    permission_required = (
        CAN_EDIT_TAXPAYER_PERM,
        CAN_EDIT_TAXPAYER_BANK_ACCOUNT_PERM,
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        taxpayer = get_object_or_404(TaxPayer, id=self.kwargs['taxpayer_id'])
        context['taxpayer_id'] = taxpayer.id
        bank_account = get_object_or_404(BankAccount, pk=self.kwargs['bank_id'], taxpayer=taxpayer)
        taxpayer = TaxPayerArgentina.objects.get(pk=context['taxpayer_id'])
        form = context['form']
        form.fields['bank_cbu_file'].initial = bank_account.bank_cbu_file
        return context

    def handle_no_permission(self):
        return HttpResponseRedirect(Http404)

    def get_success_url(self, **kwargs):
        taxpayer_id = BankAccount.objects.get(pk=self.kwargs['bank_id']).taxpayer.id
        return reverse('supplier-details', kwargs={'taxpayer_id': taxpayer_id})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if request.user.is_supplier:
            taxpayer_to_compare = TaxPayerArgentina.objects.get(pk=kwargs['taxpayer_id'])
            model_to_compare = BankAccount.objects.get(taxpayer_id=kwargs['taxpayer_id'])
            text_to_coment = reports.get_field_changes(form, ['bank_cbu_file'], model_to_compare)
            TaxpayerComment.objects.create(user=request.user, message=text_to_coment, taxpayer=taxpayer_to_compare)
            taxpayer = TaxPayer.objects.get(pk=self.kwargs['taxpayer_id'])
            taxpayer.set_changes_pending_taxpayer()
            taxpayer.save()
        return super().post(request, *args, **kwargs)


class TaxpayerHistory(UserLoginPermissionRequiredMixin, ListView):
    model = TaxPayerArgentina
    template_name = 'supplier_app/AP/taxpayer-history-list.html'
    permission_required = CAN_VIEW_TAXPAYER_HISTORY_PERM

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['taxpayer_history'] = TaxPayerArgentina.history.filter(id=self.kwargs['taxpayer_id'])
        context['is_AP'] = self.request.user.is_AP
        context['date_format'] = str(DATE_FORMAT)
        for taxpayer in context['taxpayer_history'].values():
            context['address_history'] = Address.history.filter(taxpayer_id=taxpayer.get('id'))
            context['bank_history'] = BankAccount.history.filter(taxpayer_id=taxpayer.get('id'))
        return context


class TaxpayerCommentView(UserLoginPermissionRequiredMixin, TaxPayerPermissionMixin, CreateView):
    model = TaxpayerComment
    fields = ['message']
    template_name = 'supplier_app/comments.html'
    permission_required = CAN_EDIT_TAXPAYER_PERM

    def handle_no_permission(self):
        return HttpResponseRedirect(Http404)

    def form_valid(self, form):
        form = self.set_required_fields(form)
        action = self.request.POST['action']
        taxpayer = get_object_or_404(TaxPayer, pk=self.kwargs['taxpayer_id'])
        if self.request.user.is_AP:
            taxpayer.new_comment_from_ap = True
            taxpayer.save()
            if action == TAXPAYER_STATUS_CHANGE_REQUIRED:
                run_strategy_taxpayer_status(action, taxpayer, self.request)
        elif self.request.user.is_supplier:
            taxpayer.new_comment_from_supplier = True
            taxpayer.save()

        return super().form_valid(form)

    def form_invalid(self, forms):
        messages.error(
            self.request,
            TAXPAYER_COMMENT_EMPTY,
        )
        return HttpResponseRedirect(reverse('supplier-details', kwargs=self.kwargs))

    def set_required_fields(self, form):
        taxpayer = get_object_or_404(TaxPayer, pk=self.kwargs['taxpayer_id'])
        form.instance.taxpayer = taxpayer
        form.instance.user = self.request.user
        return form

    def get_success_url(self):
        return reverse('supplier-details', kwargs=self.kwargs)


@transaction.atomic
def company_invite(request, company=None):
    try:
        old_language = translation.get_language()
        language = request.POST['language']
        translation.activate(language)
        email = [request.POST['email']]
        if not company:
            company_id = request.POST['company_id']
            company = Company.objects.get(pk=company_id)
        company_unique_token = CompanyUniqueToken(company=company)
        company_unique_token.assing_company_token
        company_unique_token.save()
        token = company_unique_token.token
        id_ebentity = EBEntityCompany.objects.get(company=company).eb_entity_id
        eb_entity = EBEntity.objects.get(pk=id_ebentity)
        company_invitation_notification(company, token, email, language, eb_entity.eb_name)
        messages.success(request, EMAIL_SUCCESS_MESSAGE)
    except CouldNotSendEmailError:
        messages.error(request, EMAIL_ERROR_MESSAGE)
    finally:
        translation.activate(old_language)
        return redirect('company-list-deprecated') if request.user.is_AP else redirect('company-list')


def company_join(request, *args, **kwargs):
    company_unique_token = _get_company_unique_token_from_token(kwargs['token'])
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/?next={}'.format(request.get_full_path()))
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


@permission_required(COMPANY_USER_CAN_APPROVE_PERM, raise_exception=True)
def change_taxpayer_status(request, taxpayer_id):
    try:
        taxpayer = TaxPayer.objects.get(pk=taxpayer_id)
        action = request.POST['action']
        run_strategy_taxpayer_status(action, taxpayer, request)
    except ObjectDoesNotExist:
        messages.error(request, TAXPAYER_NOT_EXISTS_MESSAGE)
    except CouldNotSendEmailError:
        messages.error(request, EMAIL_ERROR_MESSAGE)
    except NoWorkdayIDException:
        messages.error(request, TAXPAYER_WITHOUT_WORKDAY_ID_MESSAGE)
    except TaxpayerUniqueWorkdayId:
        messages.error(request, TAXPAYER_WORKDAY_UNIQUE_ERROR)
    finally:
        return redirect(reverse(
            'supplier-details',
            kwargs={
                'taxpayer_id': taxpayer_id
            }
        ))


class GeneratePdf(UserLoginPermissionRequiredMixin, TaxPayerPermissionMixin, TemplateView):
    template_name = 'supplier_app/html-to-pdf-page.html'
    permission_required = (CAN_VIEW_TAXPAYER_PERM)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = TaxPayer.objects.get(pk=self.kwargs['taxpayer_id']).company
        context['company'] = company
        context['buyer'] = InvitingBuyer.objects.get(company=company.id)
        supplier = TaxPayerArgentina.history.filter(id=self.kwargs['taxpayer_id'])
        context['supplier'] = supplier[len(supplier)-1]
        approved_object_query = TaxPayer.history.filter(id=self.kwargs['taxpayer_id'], taxpayer_state='APPROVED')
        approved_object = None
        context['approved_by'] = None
        if len(approved_object_query) > 0:
            approved_object = approved_object_query[0]
            context['approved_by'] = User.objects.get(pk=approved_object.history_user_id)
        context['approved_object'] = approved_object
        context['taxpayer'] = get_object_or_404(TaxPayer, pk=self.kwargs['taxpayer_id']).get_taxpayer_child()
        context['taxpayer_address'] = context['taxpayer'].address_set.get()
        context['taxpayer_contact'] = context['taxpayer'].contactinformation_set.get()
        context['taxpayer_bank_account'] = context['taxpayer'].bankaccount_set.get()
        return context

    def get(self, request, *args, **kwargs):
        pdf = render_to_pdf('supplier_app/html-to-pdf-page.html', self.get_context_data())
        return HttpResponse(pdf, content_type='application/pdf')


class BuyerTaxpayersList(UserLoginPermissionRequiredMixin, ListView):
    model = TaxPayerArgentina
    template_name = 'supplier_app/Buyer/taxpayer_list.html'
    permission_required = (
        CAN_CREATE_COMPANY_PERM,
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_list = list(Company.objects.all())
        taxpayereb_list = context['taxpayerebentity_list']
        for taxpayereb in taxpayereb_list:
            for company in company_list:
                if taxpayereb.taxpayer.company == company:
                    company_list.remove(company)
        context['company_list'] = company_list
        return context

    def get_queryset(self):
        queryset = TaxPayerEBEntity.objects.all()
        return queryset


@permission_required_decorator(CAN_VIEW_TAXPAYER_PERM)
def export_to_xlsx_taxpayer(request):
    queryset = TaxPayerFilter(request.GET, queryset=TaxPayer.objects.all()).qs
    params = ExcelReportInputParams(
        model=queryset,
        tab_name='Taxpayer',
        headers_attrs=EXPORT_TO_XLS_TAXPAYER,
    )
    xls_file = generate_xls(params)

    return generate_response_xls(xls_file, 'Taxpayer')
