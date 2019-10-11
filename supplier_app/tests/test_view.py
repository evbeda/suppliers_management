from http import HTTPStatus
from os import path
from shutil import rmtree
from unittest.mock import MagicMock

from django.core.files import File
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import Client, RequestFactory, TestCase
from django.utils.datastructures import MultiValueDict
from parameterized import parameterized

from supplier_app.forms import (AddressCreateForm, BankAccountCreateForm,
                                TaxPayerCreateForm, TaxPayerEditForm)
from supplier_app.models import (Address, BankAccount, Company, TaxPayer,
                                 TaxPayerArgentina)
from supplier_app.tests import (get_bank_info_example,
                                taxpayer_creation_POST_factory,
                                taxpayer_edit_POST_factory)
from supplier_app.tests.factory_boy import (AddressFactory, BankAccountFactory,
                                            CompanyFactory,
                                            CompanyUserPermissionFactory,
                                            TaxPayerArgentinaFactory)
from supplier_app.views import (ApTaxpayers, CreateTaxPayerView,
                                EditAddressView, EditBankAccountView,
                                EditTaxpayerView, SupplierDetailsView,
                                SupplierHome)
from users_app.factory_boy import UserFactory
from users_app.models import User


class TestCreateTaxPayer(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50
        self.bank_info = get_bank_info_example("CITIBANK N.A.")
        self.create_taxpayer_view = CreateTaxPayerView()
        self.company = CompanyFactory(
            name='FakeCompany',
            description='Best catering worldwide'
        )
        self.user_with_eb_social = UserFactory(email='nicolas')
        self.client.force_login(self.user_with_eb_social)
        self.companyuserpermission = CompanyUserPermissionFactory(
            company=self.company,
            user=self.user_with_eb_social
        )
        self.POST = taxpayer_creation_POST_factory(
            self.file_mock,
            self.bank_info
        )

    def tearDown(self):
        if self.file_mock and path.exists(
            'file/{}'.format(self.file_mock.name)
        ):
            rmtree('file')

    def _get_example_forms(self):
        FORM_POST = QueryDict('', mutable=True)
        FORM_POST.update(self.POST)
        forms = {
            'address_form': AddressCreateForm(data=FORM_POST),
            'bankaccount_form': BankAccountCreateForm(
                data=FORM_POST,
                files=self._get_request_FILES()
            ),
            'taxpayer_form': TaxPayerCreateForm(
                data=FORM_POST,
                files=self._get_request_FILES()
                )
        }
        return forms

    def _get_request_FILES(
        self,
        afip_file=None,
        witholding_taxes_file=None,
        bank_cbu_file=None
    ):
        return MultiValueDict({
            'taxpayer_form-afip_registration_file': [
                afip_file or self.file_mock
            ],
            'taxpayer_form-witholding_taxes_file': [
                witholding_taxes_file or self.file_mock
            ],
            'bankaccount_form-bank_cbu_file': [
                bank_cbu_file or self.file_mock
            ],
        })

    def test_get_success_url_should_redirect_to_home(self):
        self.assertEqual(
            '/suppliersite/supplier',
            self.create_taxpayer_view.get_success_url()
            )

    def _get_taxpayer_creation_request(self):
        request = self.factory.get(
            '/suppliersite/supplier/taxpayer/create',
            )
        request.user = self.user_with_eb_social
        return request

    def test_form_valid_method_should_save_taxpayer_address_bankaccount(self):
        taxpayer_qty_before_creation = len(TaxPayer.objects.all())
        bank_account_qty_before_creation = len(BankAccount.objects.all())
        address_qty_before_creation = len(Address.objects.all())
        taxpayer_creation_forms = self._get_example_forms()

        self.create_taxpayer_view.request = \
            self._get_taxpayer_creation_request()
        self.create_taxpayer_view.form_valid(taxpayer_creation_forms)

        taxpayer_qty_after_creation = len(TaxPayer.objects.all())
        bank_account_qty_after_creation = len(BankAccount.objects.all())
        address_qty_after_creation = len(Address.objects.all())

        self.assertGreater(
            taxpayer_qty_after_creation,
            taxpayer_qty_before_creation
        )
        self.assertGreater(
            bank_account_qty_after_creation,
            bank_account_qty_before_creation
        )
        self.assertGreater(
            address_qty_after_creation,
            address_qty_before_creation
        )

    def test_address_bankaccount_should_be_related_with_taxpayer(self):
        taxpayer_creation_forms = self._get_example_forms()

        self.create_taxpayer_view.request = \
            self._get_taxpayer_creation_request()
        self.create_taxpayer_view.form_valid(taxpayer_creation_forms)
        address = Address.objects.last()
        bankaccount = BankAccount.objects.last()
        taxpayer_created = TaxPayer.objects.last()
        self.assertEqual(
            taxpayer_created,
            address.taxpayer
        )
        self.assertEqual(
            taxpayer_created,
            bankaccount.taxpayer
        )


class TestTaxpayerList(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.company = CompanyFactory(
            name='Supra',
            description='Best catering worldwide'
        )
        self.taxpayer_ar = TaxPayerArgentinaFactory(
            business_name='Eventbrite',
            workday_id='12345',
            taxpayer_state='PENDING',
            cuit='20-31789965-3',
            company=self.company,
        )

        self.user_with_social_evb = UserFactory(email='nahuel')

        self.companyuserpermission = CompanyUserPermissionFactory(
            company=self.company,
            user=self.user_with_social_evb
        )

    def test_get_taxpayers_child(self):
        request = self.factory.get('/suppliersite/home')
        request.user = self.user_with_social_evb

        supplier_home = SupplierHome()
        supplier_home.request = request
        taxpayer_list = supplier_home.get_taxpayers()

        self.assertEqual(
            type(taxpayer_list[0]),
            TaxPayerArgentina
        )
        self.assertGreaterEqual(len(taxpayer_list), 1)


class TestTaxpayerApList(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.company1 = CompanyFactory(
            name='Empresa 1',
            description='Descripcion de la empresa 1'
        )
        self.company2 = CompanyFactory(
            name='Empresa 2',
            description='Descripcion de la empresa 2'
        )

        self.taxpayer_ar1 = TaxPayerArgentinaFactory(
            business_name='Pyme 1',
            workday_id='1',
            taxpayer_state='PENDING',
            cuit='20-31789965-3',
            company=self.company1,
        )
        self.taxpayer_ar2 = TaxPayerArgentinaFactory(
            business_name='Pyme 2',
            workday_id='2',
            taxpayer_state='CHANGE REQUIRED',
            cuit='20-39237968-5',
            company=self.company2,
        )

        self.user_ap = User.objects.create_user(email='ap@eventbrite.com')
        self.user_with_social_evb1 = UserFactory(email='nahuel')
        self.user_with_social_evb2 = UserFactory(email='nicolas')

        self.companyuserpermission1 = CompanyUserPermissionFactory(
            company=self.company1,
            user=self.user_with_social_evb1
        )
        self.companyuserpermission2 = CompanyUserPermissionFactory(
            company=self.company2,
            user=self.user_with_social_evb2
        )

    def test_get_taxpayers_with_status_PENDING_or_REQUESTCHANGE_in_ap_site(self):
        request = self.factory.get('/suppliersite/ap')
        request.user = self.user_ap

        ap_home = ApTaxpayers()
        ap_home.request = request

        response_queryset = ap_home.get_queryset()

        self.assertIn(self.taxpayer_ar1, response_queryset)
        self.assertIn(self.taxpayer_ar2, response_queryset)

    def test_get_taxpayers_list_success(self):
        request = self.factory.get('/suppliersite/ap')
        request.user = self.user_ap

        response = ApTaxpayers()
        response = ApTaxpayers.as_view()(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual('AP_app/ap-taxpayers.html', response.template_name[0])


class TestTaxpayerApDetails(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50
        self.ap_user = User.objects.create_user(email='ap@eventbrite.com')

        self.company_user_permission = CompanyUserPermissionFactory()
        self.taxpayer = TaxPayerArgentinaFactory(
            company=self.company_user_permission.company,
            afip_registration_file=self.file_mock,
            witholding_taxes_file=self.file_mock,
        )
        self.address = AddressFactory(taxpayer=self.taxpayer)
        self.bank_account = BankAccountFactory(
            taxpayer=self.taxpayer,
            bank_cbu_file=self.file_mock
            )

        self.kwargs = {
            'taxpayer_id': self.taxpayer.id,
        }

    def test_get_taxpayers_details_in_ap_site(self):

        request = self.factory.get(
            '/suppliersite/taxpayer/{}/details/'.format(self.taxpayer.id)
        )

        request.user = self.ap_user

        response = SupplierDetailsView.as_view()(request, **self.kwargs)

        self.assertEqual(
            self.taxpayer,
            response.context_data['taxpayer']
        )
        self.assertEqual(
            self.taxpayer,
            response.context_data['taxpayer_address'].taxpayer
        )
        self.assertEqual(
            self.taxpayer,
            response.context_data['taxpayer_bank_account'].taxpayer
        )

    def test_get_taxpayers_details_success(self):

        request = self.factory.get(
            '/suppliersite/taxpayer/{}/details/'.format(self.taxpayer.id)
            )

        request.user = self.ap_user

        response = SupplierDetailsView.as_view()(request, **self.kwargs)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_404_when_try_to_get_taxpayer_details_with_invalid_id(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse('supplier-details', kwargs={'taxpayer_id': 999}),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_taxpayer_detail_template(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse('supplier-details', kwargs={'taxpayer_id': self.taxpayer.id}),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response,
            "CBU"
        )
        self.assertContains(
            response,
            'AFIP certificate'
        )
        self.assertContains(
            response,
            'Withholding taxes'
        )

    def test_details_view_has_approve_button_when_AP_has_set_workday_id(self):
        request = self.factory.get(
            '/suppliersite/ap/taxpayer/{}/details/'.format(
                self.taxpayer.id
            ),
        )
        request.user = self.ap_user
        response = SupplierDetailsView.as_view()(request, **self.kwargs)

        self.assertContains(
            response, 'Approve'
        )

    def test_details_view_doesnt_have_approve_button_when_AP_hasnt_set_workday_id(self):
        taxpayer = TaxPayerArgentinaFactory(
            workday_id="",
            afip_registration_file=self.file_mock,
            witholding_taxes_file=self.file_mock,
        )
        AddressFactory(taxpayer=taxpayer)
        BankAccountFactory(
            taxpayer=taxpayer,
            bank_cbu_file=self.file_mock
        )
        self.client.force_login(self.ap_user)

        response = self.client.get(
            reverse("supplier-details", kwargs={'taxpayer_id': taxpayer.id})
        )

        self.assertNotContains(
            response, 'Approve',
        )

    def test_taxpayer_details_view_doesnt_show_edit_button_when_the_taxpayer_has_status_denied(self):
        taxpayer = TaxPayerArgentinaFactory(
            taxpayer_state="DENIED",
            afip_registration_file=self.file_mock,
            witholding_taxes_file=self.file_mock,
        )
        AddressFactory(taxpayer=taxpayer)
        BankAccountFactory(
            taxpayer=taxpayer,
            bank_cbu_file=self.file_mock
        )
        self.client.force_login(self.ap_user)

        response = self.client.get(
            reverse("supplier-details", kwargs={'taxpayer_id': taxpayer.id})
        )

        self.assertNotContains(
            response, 'Edit',
        )

    @parameterized.expand([
        ("APPROVE", "1"),
        ("DENIED", "2"),
        ("DENIED", ""),
    ])
    def test_taxpayer_details_view_doesnt_show_approve_and_deny_button_if_the_taxpayer_is_already_approved_or_denied(self, status, workday_id):
        taxpayer = TaxPayerArgentinaFactory(
            taxpayer_state=status,
            workday_id=workday_id,
            afip_registration_file=self.file_mock,
            witholding_taxes_file=self.file_mock,
        )
        AddressFactory(taxpayer=taxpayer)
        BankAccountFactory(
            taxpayer=taxpayer,
            bank_cbu_file=self.file_mock
        )

        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse("supplier-details", kwargs={'taxpayer_id': taxpayer.id})
        )

        self.assertNotContains(
            response, 'Approve'
        )

        self.assertNotContains(
            response, 'Deny'
        )


class TestEditTaxPayerInfo(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.ap_user = User.objects.create_user(email='ap@eventbrite.com')

        self.taxpayer = TaxPayerArgentinaFactory()
        self.taxpayer_detail_url = 'supplier-details'
        self.edit_taxpayer_view = EditTaxpayerView()

        self.TAXPAYER_POST = taxpayer_edit_POST_factory()
        self.kwargs = {
            'taxpayer_id': self.taxpayer.id,
        }
        self.taxpayer_id = self.taxpayer.id

    def test_get_success_url_should_redirect_to_details_view_when_click_in_update_button(self):
        request = self.factory.get(
            '/suppliersite/ap/taxpayer/{}/update/taxpayer_info/'.format(
                self.taxpayer_id
            ),
        )
        response = EditTaxpayerView.as_view()(request, **self.kwargs)
        self.assertEqual(
            'AP_app/edit-taxpayer-information.html',
            response.template_name[0]
        )

    def test_post_edit_taxpayer_info(self):
        request = self.factory.post(
            '/suppliersite/ap/taxpayer/{}/update/taxpayer_info/'.format(
                self.taxpayer_id
            ),
            data=self.TAXPAYER_POST
        )
        response = EditTaxpayerView.as_view()(request, **self.kwargs)

        self.assertEqual(
            reverse(
                self.taxpayer_detail_url,
                kwargs=self.kwargs
            ),
            response.url
        )

    @parameterized.expand([
        (
            taxpayer_edit_POST_factory(
                workday_id="1",
                business_name="EB USA",
                cuit="20-3123214-1",
            ),
            ["workday_id", "business_name", "cuit"],
            ["1", "EB USA", "20-3123214-1"]
        ),
        (
            taxpayer_edit_POST_factory(
                cuit="20-3123214-1",
            ),
            ["cuit", "business_name"],
            ["20-3123214-1", "EB ARG"]
        ),
        (
            taxpayer_edit_POST_factory(
                payment_term=1,
            ),
            ["payment_term"],
            [30]
        )
    ])
    def test_form_valid_method_should_update_taxpayer_info(
        self,
        taxpayer_post_update,
        fields_changed,
        value_expected
    ):
        before_update = len(TaxPayer.objects.all())

        TAXPAYER_POST_UPDATE = taxpayer_post_update
        QUERY_FORM_TAXPAYER_POST_UPDATE = QueryDict('', mutable=True)
        QUERY_FORM_TAXPAYER_POST_UPDATE.update(
            TAXPAYER_POST_UPDATE
        )

        edit_taxpayer_view = EditTaxpayerView()
        edit_taxpayer_view.kwargs = {
            'taxpayer_id': self.taxpayer.id
        }

        form_taxpayer = TaxPayerEditForm(data=QUERY_FORM_TAXPAYER_POST_UPDATE)
        self.assertTrue(form_taxpayer.is_valid())

        edit_taxpayer_view.form_valid(form_taxpayer)

        after_update = len(TaxPayer.objects.all())

        taxpayer = TaxPayerArgentina.objects.get(pk=self.taxpayer_id)
        self.assertEqual(before_update, after_update)
        for index, attribute in enumerate(fields_changed):
            self.assertEqual(
                getattr(taxpayer, attribute), value_expected[index]
            )


class TestEditAddressInfo(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.taxpayer = TaxPayerArgentinaFactory()
        self.address = AddressFactory(taxpayer=self.taxpayer)
        self.address_edit_url = 'address-update'
        self.taxpayer_detail_url = 'supplier-details'
        self.ADDRESS_POST = {
            'address_form-street': 'San Martin',
            'address_form-number': '21312',
            'address_form-zip_code': '123',
            'address_form-city': 'Mendoza',
            'address_form-state': 'Mendoza',
            'address_form-country': 'Argentina',
        }
        self.kwargs_taxpayer = {
            'taxpayer_id': self.taxpayer.id,
        }
        self.kwargs_address = {
            'address_id': self.address.id
        }
        self.taxpayer_id = self.taxpayer.id

    def test_GET_edit_address_view(self):
        request = self.factory.get(
            reverse(
                self.address_edit_url,
                kwargs=self.kwargs_address
            )
        )
        response = EditAddressView.as_view()(request, **self.kwargs_address)
        self.assertEqual(
            'AP_app/edit-address-information.html',
            response.template_name[0]
        )

    def test_post_edit_address_info(self):
        request = self.factory.post(
            reverse(
                self.address_edit_url,
                kwargs=self.kwargs_address
            ),
            data=self.ADDRESS_POST
        )
        response = EditAddressView.as_view()(request, **self.kwargs_address)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(
            reverse(
                self.taxpayer_detail_url,
                kwargs=self.kwargs_taxpayer
            ),
            response.url
        )


class TestEditBankAccountInfo(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.taxpayer = TaxPayerArgentinaFactory()
        self.bank_account = BankAccountFactory(taxpayer=self.taxpayer)
        self.bank_update_url = 'bank-account-update'

        self.BANK_ACCOUNT_POST = {
            'bank_info': get_bank_info_example("CITIBANK N.A."),
            'bank_account_number': '123214',
        }

        self.taxpayer_detail_url = 'supplier-details'
        self.kwargs_taxpayer = {
            'taxpayer_id': self.taxpayer.id,
        }
        self.kwargs_bank = {
            'bank_id': self.bank_account.id,
        }

        self.taxpayer_id = self.taxpayer.id

    def test_GET_bank_account_edit_view(self):
        request = self.factory.get(
            reverse(self.bank_update_url, kwargs=self.kwargs_bank)
        )
        response = EditBankAccountView.as_view()(request, **self.kwargs_bank)

        self.assertEqual(
            HTTPStatus.OK,
            response.status_code
        )
        self.assertEqual(
            'AP_app/edit-bank-account-information.html',
            response.template_name[0]
        )

    def test_post_edit_bank_account_info(self):
        response = self.client.post(
            reverse(
                self.bank_update_url,
                kwargs=self.kwargs_bank
            ),
            self.BANK_ACCOUNT_POST
        )
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(
            reverse(
                self.taxpayer_detail_url,
                kwargs=self.kwargs_taxpayer
            ),
            response.url
        )


class TestCompanyCreateView(TestCase):
    def setUp(self):
        self.company_constants = {
            'name': 'Eventbrite',
            'description':
                'Bringing the world together through live experiences',
        }
        self.user = UserFactory(email="ap@eventbrite.com")
        self.client = Client()
        self.client.force_login(self.user)

    def _make_post(self):
        return self.client.post(
            '/suppliersite/ap/company/create',
            self.company_constants,
            follow=True,
        )

    def test_get_template(self):
        response = self.client.get('/suppliersite/ap/company/create')
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(
            'AP_app/company_creation.html',
            response.template_name[0]
        )

    def test_valid_company_creation(self):
        self._make_post()
        self.assertEqual(
            Company.objects.last().name,
            self.company_constants['name']
        )

    def test_valid_redirection_after_company_creation(self):
        response = self._make_post()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.redirect_chain[0][0],
            '/suppliersite/ap'
        )


class TestApprovalRefuse(TestCase):
    def setUp(self):
        self.taxpayer = TaxPayerArgentinaFactory()
        self.client = Client()
        self.ap_user = User.objects.create_user(email='ap@eventbrite.com')
        self.client.force_login(self.ap_user)
        self.approve_url = 'approve-taxpayer'
        self.deny_url = 'deny-taxpayer'
        self.kwargs = {
            'taxpayer_id' : self.taxpayer.id
        }

    def test_redirect_to_ap_home_when_approve_a_supplier(self):
        response = self.client.post(
            reverse(
                self.approve_url,
                kwargs=self.kwargs
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/suppliersite/ap')

    def test_change_taxpayer_status_to_ACTIVE_when_clicking_aprove_button(self):
        self.client.post(
            reverse(
                self.approve_url,
                kwargs=self.kwargs
            )
        )

        self.assertEqual(
            TaxPayer.objects.get(pk=self.taxpayer.id).taxpayer_state,
            'ACTIVE'
        )

    def test_redirect_to_ap_home_when_deny_a_supplier(self):
        response = self.client.post(
            reverse(
                self.deny_url,
                kwargs=self.kwargs
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/suppliersite/ap')

    def test_change_taxpayer_status_to_DENIED_when_clicking_deny_button(self):
        self.client.post(
            reverse(
                self.deny_url,
                kwargs=self.kwargs
            )
        )

        self.assertEqual(
            TaxPayer.objects.get(pk=self.taxpayer.id).taxpayer_state,
            'DENIED'
        )
