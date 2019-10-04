from http import HTTPStatus
from os import (
    path,
    remove,
)
from shutil import rmtree
from parameterized import parameterized
from unittest import mock
from unittest.mock import patch
from unittest.mock import MagicMock

from django.http import (
    HttpResponseRedirect,
    QueryDict
)
from django.core.files import File
from django.test import (
    TestCase,
    RequestFactory,
    Client
)
from django.core.files import File as DjangoFile
from django.core.urlresolvers import (
    resolve,
    reverse,
    reverse_lazy,
)

from social_django.models import UserSocialAuth
from supplier_app.factory_boy import (
    AddressFactory,
    BankAccountFactory,
    CompanyUserPermissionFactory,
    TaxPayerArgentinaFactory,
)
from django.utils.datastructures import MultiValueDict

from supplier_app.forms import (
    AddressCreateForm,
    BankAccountCreateForm,
    PDFFileForm,
    TaxPayerCreateForm,
    BasePrefixCreateForm
)

from supplier_app.models import (
    Address,
    BankAccount,
    Company,
    CompanyUserPermission,
    PDFFile,
    TaxPayer,
    TaxPayerArgentina,
)

from supplier_app.views import (
    ApTaxpayers,
    CreateTaxPayerView,
    EditAddressView,
    EditBankAccountView,
    EditTaxpayerView,
    SupplierDetailsView,
    SupplierHome,
)

from users_app.models import User

GENERIC_PASSWORD = '1234'


class TestModels(TestCase):
    def setUp(self):
        self.taxpayer = {
            'business_name': 'Eventbrite',
            'workday_id': '12345',
        }
        self.company = {
            'name': 'Eventbrite',
            'description': 'Bringing the world together through live experiences',
        }
        self.user = {
            'email': 'pepe@pepe.com',
        }
        self.taxpayer_ar1 = {
            'business_name': 'Eventbrite',
            'workday_id': '12345',
            'cuit': '20-31789965-3'
        }
        self.taxpayer_ar2 = {
            'business_name': 'Cocacola',
            'workday_id': '67890',
            'taxpayer_state': 'PENDING',
            'cuit': '30-31789965-5'
        }

    def test_tax_payer_entity(self):
        company = Company.objects.create(**self.company)
        taxpayer = TaxPayer.objects.create(**self.taxpayer, company=company)
        self.assertEqual(taxpayer.business_name, 'Eventbrite')
        self.assertEqual(taxpayer.workday_id, '12345')

    def test_state_when_create_tax_payer_first_time(self):
        company = Company.objects.create(**self.company)
        taxpayer = TaxPayer.objects.create(**self.taxpayer, company=company)
        self.assertEqual(taxpayer.taxpayer_state, "PENDING")

    def test_create_child_of_tax_payer(self):
        taxpayer_ar1 = TaxPayerArgentina(**self.taxpayer_ar1)
        self.assertTrue(isinstance(taxpayer_ar1, TaxPayer))
        self.assertEqual(taxpayer_ar1.business_name, 'Eventbrite')

    def test_get_taxpayer_child(self):
        company = Company.objects.create(**self.company)
        taxpayerar = TaxPayerArgentina.objects.create(**self.taxpayer_ar1, company=company)
        self.assertEqual(
            taxpayerar.get_taxpayer_child().business_name,
            self.taxpayer_ar1['business_name']
        )

    def test_address(self):
        company = Company.objects.create(**self.company)
        taxpayer1 = TaxPayer.objects.create(**self.taxpayer, company=company)
        address = Address(
            street='Rep. del Libano',
            number='981',
            zip_code='5501',
            city='Godoy Cruz',
            state='Mendoza',
            country='Argentina',
            taxpayer=taxpayer1
        )
        self.assertEqual(
            str(address),
            "ADDRESS \n Street: {} Number: {} Zip_Code: {} City: {} State: {} Country: {}".format(
                'Rep. del Libano',
                '981',
                '5501',
                'Godoy Cruz',
                'Mendoza',
                'Argentina',
                taxpayer1
            )
        )
        self.assertEqual(address.taxpayer, taxpayer1)

    def test_bank_account(self):
        company = Company.objects.create(**self.company)
        taxpayer1 = TaxPayer.objects.create(**self.taxpayer, company=company)
        bank = BankAccount.objects.create(
            bank_name='Supervielle',
            bank_code='CA $',
            bank_account_number='44-2417027-3',
            taxpayer=taxpayer1
        )
        self.assertEqual(bank.bank_name, 'Supervielle')
        self.assertEqual(bank.taxpayer.business_name, 'Eventbrite')


class TestCreateTaxPayer(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50
        self.create_taxpayer_view = CreateTaxPayerView()
        self.company = Company.objects.create(name='FakeCompany', description='Best catering worldwide')
        self.user_with_eb_social = \
            User.objects.create_user(email='nicolas', password=GENERIC_PASSWORD)
        UserSocialAuth.objects.create(
            user=self.user_with_eb_social,
            provider='eventbrite',
            uid='1233543645',
            extra_data={
                'auth_time': 1567127106,
                'access_token': 'testToken',
                'token_type': 'bearer',
            }
        )
        self.client.force_login(self.user_with_eb_social)
        self.companyuserpermission = \
            CompanyUserPermission.objects.create(company=self.company, user=self.user_with_eb_social)
        self.POST = {
            'csrfmiddlewaretoken': '67lLxnP0Q0oDIYThiF0z7cEcuLrmJSvT1OJUH0J9RyByLxiMeghEHuGKowoq4bZa',
            'taxpayer_form-workday_id': '1',
            'taxpayer_form-business_name': 'EB ARG',
            'taxpayer_form-cuit': '20-3123214-0',
            'taxpayer_form-country': 'AR',
            'taxpayer_form-comments': 'dafsadsffasdf',
            'taxpayer_form-payment_type': 'dafsadsffasdf',
            'taxpayer_form-AFIP_registration_file': self.file_mock.name,
            'taxpayer_form-witholding_taxes_file': self.file_mock.name,
            'address_form-street': 'San Martin',
            'address_form-number': '21312',
            'address_form-zip_code': '123',
            'address_form-city': 'Mendoza',
            'address_form-state': 'Mendoza',
            'address_form-country': 'Argentina',
            'bankaccount_form-bank_bank_cbu_file': self.file_mock.name,
            'bankaccount_form-bank_name': 'Ganicia',
            'bankaccount_form-bank_code': 'Cta Cte',
            'bankaccount_form-bank_account_number': '123214',
        }

    def tearDown(self):
        if self.file_mock and path.exists('file/{}'.format(self.file_mock.name)):
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
        AFIP_file=None,
        witholding_taxes_file=None,
        bank_cbu_file=None
    ):
        return MultiValueDict({
            'taxpayer_form-AFIP_registration_file': [AFIP_file or self.file_mock],
            'taxpayer_form-witholding_taxes_file': [witholding_taxes_file or self.file_mock],
            'bankaccount_form-bank_cbu_file': [bank_cbu_file or self.file_mock],
        })

    def test_get_success_url_should_redirect_to_home(self):
        self.assertEqual(
            '/suppliersite/supplier', self.create_taxpayer_view.get_success_url()
            )

    def test_GET_taxpayer_view_should_render_3_forms(self):
        response = self.client.get('/suppliersite/supplier/taxpayer/create')
        taxpayer_form = response.context_data['taxpayer_form']
        address_form = response.context_data['address_form']
        bankaccount_form = response.context_data['bank_account_form']
        self.assertEqual(AddressCreateForm, type(address_form))
        self.assertEqual(BankAccountCreateForm, type(bankaccount_form))
        self.assertEqual(TaxPayerCreateForm, type(taxpayer_form))

    def test_valid_forms_pass_validation(self):
        forms = self._get_example_forms()
        self.assertTrue(self.create_taxpayer_view.forms_are_valid(forms))

    @parameterized.expand([
        (5000000000000000, 'bank_cbu_file'),
        (26214500, 'bank_cbu_file'),
        (27214400, 'AFIP_file'),
        (26214401, 'witholding_taxes_file')
    ]
    )
    def test_form_with_a_file_greater_than_25MB_should_be_invalid(
        self,
        param_size,
        attr
    ):
        request = self.factory.post('/suppliersite/supplier/taxpayer/create', data=self.POST)
        request.user = self.user_with_eb_social
        file_mock = MagicMock(spec=File)
        file_mock.name = 'test.pdf'
        file_mock.size = param_size
        request.FILES.update(self._get_request_FILES(**{attr: file_mock}))
        with patch(
            'supplier_app.views.CreateTaxPayerView.form_invalid',
            return_value=HttpResponseRedirect('/suppliersite/supplier')
        ) as mocked_invalid_form:
            CreateTaxPayerView.as_view()(request)
            mocked_invalid_form.assert_called()

    @parameterized.expand([
        ('test.xml', 'bank_cbu_file'),
        ('test.txt', 'bank_cbu_file'),
        ('test.exe', 'AFIP_file'),
        ('test.excel', 'witholding_taxes_file'),
    ]
    )
    def test_form_with_a_non_PDF_type_file_should_be_invalid(
        self,
        param_name,
        attr
    ):
        request = self.factory.post('/suppliersite/supplier/taxpayer/create', data=self.POST)
        request.user = self.user_with_eb_social
        file_mock = MagicMock(spec=File)
        file_mock.name = param_name
        file_mock.size = 50
        request.FILES.update(self._get_request_FILES(**{attr: file_mock}))
        with patch(
            'supplier_app.views.CreateTaxPayerView.form_invalid',
            return_value=HttpResponseRedirect('/suppliersite/supplier')
        ) as mocked_invalid_form:
            CreateTaxPayerView.as_view()(request)
            mocked_invalid_form.assert_called()

    @patch(
        'supplier_app.views.CreateTaxPayerView.form_valid',
        return_value=HttpResponseRedirect('/suppliersite/supplier')
        )
    def test_form_valid_method_should_be_called_with_an_valid_POST(self, mocked_valid_form):
        request = self.factory.post('/suppliersite/supplier/taxpayer/create', data=self.POST)
        request.user = self.user_with_eb_social
        request.FILES.update(self._get_request_FILES())
        CreateTaxPayerView.as_view()(request)
        mocked_valid_form.assert_called()

    @patch(
        'supplier_app.views.CreateTaxPayerView.form_invalid',
        return_value=HttpResponseRedirect('/suppliersite/supplier')
        )
    def test_form_invalid_method_should_be_called_with_an_invalid_POST(self, mocked_invalid_form):
        self.client.post('/suppliersite/supplier/taxpayer/create', {
            'asda': 'asd',
        })
        mocked_invalid_form.assert_called()

    def test_form_valid_method_should_save_taxpayer_address_bankaccount(self):
        forms = self._get_example_forms()
        request = self.factory.get('/suppliersite/supplier/taxpayer/create')
        request.user = self.user_with_eb_social
        self.create_taxpayer_view.request = request
        self.create_taxpayer_view.form_valid(forms)
        taxpayer = TaxPayerArgentina.objects.filter(business_name='EB ARG')
        address = Address.objects.filter(street='San Martin')
        bankaccount = BankAccount.objects.filter(bank_name='Ganicia')
        self.assertEqual(
            TaxPayerArgentina, type(taxpayer[0])
        )
        self.assertGreaterEqual(1, len(taxpayer))
        self.assertGreaterEqual(1, len(bankaccount))
        self.assertGreaterEqual(1, len(address))

    def test_address_bankaccount_should_be_related_with_taxpayer(self):
        forms = self._get_example_forms()
        request = self.factory.get('/suppliersite/home')
        request.user = self.user_with_eb_social
        self.create_taxpayer_view.request = request
        self.create_taxpayer_view.form_valid(forms)
        address = Address.objects.get(street='San Martin')
        bankaccount = BankAccount.objects.get(bank_name='Ganicia')
        self.assertEqual('Name:EB ARG Status:PENDING', str(address.taxpayer))
        self.assertEqual('Name:EB ARG Status:PENDING', str(bankaccount.taxpayer))


class TestBase(TestCase):
    def setUp(self):
        super(TestBase, self).setUp()
        self.client = Client()
        self.file_mock = []

    def tearDown(self):
        if(
            self.file_mock and path.exists('file/' + self.file_mock.name)
        ):
            remove('file/' + self.file_mock.name)


class ViewTest(TestBase):

    def test_create_file_exists(self):
        view = resolve('/suppliersite/files/create')
        self.assertEqual(view.view_name, 'create-file')

    def test_pdf_file_submission(self):
        self.file_mock = mock.MagicMock(spec=DjangoFile)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50
        data = {
            'pdf_file': self.file_mock
        }
        self.client.post(
            reverse(
                'create-file',
            ),
            data
        )
        result = PDFFile.objects.get()
        self.assertEquals(result.pdf_file.name, 'file/test.pdf')

    def test_pdf_file_redirect(self):
        self.file_mock = mock.MagicMock(spec=DjangoFile)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50
        data = {
            'pdf_file': self.file_mock
        }
        response = self.client.post(
            reverse(
                'create-file',
            ),
            data
        )
        self.assertEquals(response.status_code, HTTPStatus.FOUND)


class ModelTest(TestBase):

    def test_model_file_type_valid(self):
        self.file_mock = mock.MagicMock(spec=DjangoFile)
        self.file_mock.name = 'test.pdf'
        pdf_file = PDFFile.objects.create(pdf_file=self.file_mock)
        self.assertTrue('.pdf' in pdf_file.pdf_file.name)


class FormTest(TestBase):

    @parameterized.expand([
        ('test.pdf', 20, True),
        ('test.xml', 20, False),
        ('test.pdf', 500000000, False),
        ('test.xml', 500000000, False),

    ])
    def test_form_is_valid(self, name_file, size_file, expected):
        self.file_mock = mock.MagicMock(spec=DjangoFile)
        self.file_mock.name = name_file
        self.file_mock.size = size_file
        form = PDFFileForm(
            data={},
            files={
                'pdf_file': self.file_mock,
            }
        )
        self.assertEqual(form.is_valid(), expected)


class TestTaxpayerList(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.company = Company.objects.create(
            name='Supra',
            description='Best catering worldwide'
        )
        self.taxpayer_ar = TaxPayerArgentina.objects.create(
            business_name='Eventbrite',
            workday_id='12345',
            taxpayer_state='PENDING',
            cuit='20-31789965-3',
            company=self.company,
        )

        self.user_with_social_evb = \
            User.objects.create_user(email='nahuel', password="1234asdf")
        UserSocialAuth.objects.create(
            user=self.user_with_social_evb,
            provider='eventbrite',
            uid='1234567890',
            extra_data={
                'auth_time': 1567127106,
                'access_token': 'testToken',
                'token_type': 'bearer',
            }
        )

        self.companyuserpermission = CompanyUserPermission.objects.create(
            company=self.company,
            user=self.user_with_social_evb
        )

    def test_get_taxpayers_child(self):
        request = self.factory.get('/suppliersite/home')
        request.user = self.user_with_social_evb

        supplier_home = SupplierHome()
        supplier_home.request = request
        taxpayer_child = supplier_home.get_taxpayers()

        self.assertEqual(str(taxpayer_child), '[<TaxPayerArgentina: Name:Eventbrite Status:PENDING>]')
        self.assertEqual(len(taxpayer_child), 1)


class TestTaxpayerApList(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.company1 = Company.objects.create(
            name='Empresa 1',
            description='Descripcion de la empresa 1'
        )
        self.company2 = Company.objects.create(
            name='Empresa 2',
            description='Descripcion de la empresa 2'
        )

        self.taxpayer_ar1 = TaxPayerArgentina.objects.create(
            business_name='Pyme 1',
            workday_id='1',
            taxpayer_state='PENDING',
            cuit='20-31789965-3',
            company=self.company1,
        )
        self.taxpayer_ar2 = TaxPayerArgentina.objects.create(
            business_name='Pyme 2',
            workday_id='2',
            taxpayer_state='CHANGE REQUIRED',
            cuit='20-39237968-5',
            company=self.company2,
        )

        self.user_with_social_evb1 = \
            User.objects.create_user(email='nahuel', password="1234asdf")
        UserSocialAuth.objects.create(
            user=self.user_with_social_evb1,
            provider='eventbrite',
            uid='1234567890',
            extra_data={
                'auth_time': 1567127106,
                'access_token': 'testToken',
                'token_type': 'bearer',
            }
        )

        self.user_with_social_evb2 = \
            User.objects.create_user(email='nicolas', password="nicolas123")
        UserSocialAuth.objects.create(
            user=self.user_with_social_evb2,
            provider='eventbrite',
            uid='0987654321',
            extra_data={
                'auth_time': 1567127106,
                'access_token': 'testToken',
                'token_type': 'bearer',
            }
        )

        self.companyuserpermission1 = CompanyUserPermission.objects.create(
            company=self.company1,
            user=self.user_with_social_evb1
        )
        self.companyuserpermission2 = CompanyUserPermission.objects.create(
            company=self.company2,
            user=self.user_with_social_evb2
        )

    def test_get_taxpayers_with_status_pendindg_or_request_changed_in_ap_site(self):
        request = self.factory.get('/suppliersite/ap')
        user_ap = User.objects.create_user(email='ap@eventbrite.com')
        request.user = user_ap

        ap_home = ApTaxpayers()
        ap_home.request = request

        response_queryset = ap_home.get_queryset()

        self.assertIn(self.taxpayer_ar1, response_queryset)
        self.assertIn(self.taxpayer_ar2, response_queryset)

    def test_get_taxpayers_list_success(self):
        request = self.factory.get('/suppliersite/ap')
        user_ap = User.objects.create_user(email='ap@eventbrite.com')
        request.user = user_ap

        response = ApTaxpayers()
        response = ApTaxpayers.as_view()(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestTaxpayerApDetails(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

        self.ap_user = User.objects.create_user(email='ap@eventbrite.com')

        self.company_user_permission = CompanyUserPermissionFactory()
        self.taxpayer = TaxPayerArgentinaFactory(company=self.company_user_permission.company)
        self.address = AddressFactory(taxpayer=self.taxpayer)
        self.bank_account = BankAccountFactory(taxpayer=self.taxpayer)

        self.kwargs = {
            'taxpayer_id': self.taxpayer.id,
        }

    def test_get_taxpayers_details_in_ap_site(self):

        request = self.factory.get('/suppliersite/taxpayer/{}/details/'.format(self.taxpayer.id))

        request.user = self.ap_user

        response = SupplierDetailsView.as_view()(request, **self.kwargs)

        self.assertEqual(self.taxpayer, response.context_data['taxpayer'])
        self.assertEqual(self.taxpayer, response.context_data['taxpayer_address'].taxpayer)
        self.assertEqual(self.taxpayer, response.context_data['taxpayer_bank_account'].taxpayer)

    def test_get_taxpayers_details_success(self):

        request = self.factory.get('/suppliersite/taxpayer/{}/details/'.format(self.taxpayer.id))

        request.user = self.ap_user

        response = SupplierDetailsView.as_view()(request, **self.kwargs)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_404_when_try_to_get_taxpayer_details_with_invalid_id(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse('supplier-details', kwargs={'taxpayer_id': 999}),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestCreatePrefixForm(TestCase):

    def setUp(self):
        self.POST = {
            'taxpayer_form-workday_id': '1',
            'taxpayer_form-business_name': 'EB ARG',
            'taxpayer_form-cuit': '20-3123214-0',
            'taxpayer_form-country': 'AR',
            'taxpayer_form-comments': 'dafsadsffasdf',
            'taxpayer_form-payment_type': 'dafsadsffasdf',
            'taxpayer_form-AFIP_registration_file': '',
            'taxpayer_form-witholding_taxes_file': '',
            'address_form-street': 'San Martin',
            'address_form-number': '21312',
            'address_form-zip_code': '123',
            'address_form-city': 'Mendoza',
            'address_form-state': 'Mendoza',
            'address_form-country': 'Argentina',
            'bankaccount_form-bank_cbu_file': '',
            'bankaccount_form-bank_name': 'Ganicia',
            'bankaccount_form-bank_code': 'Cta Cte',
            'bankaccount_form-account_number': '123214',
        }

    def test_form_without_prefix_should_throw_exception(self):
        with self.assertRaises(ValueError):
            BasePrefixCreateForm()

    def test_form_with_prefix_only_save_data_with_that_prefix(self):
        data = QueryDict('', mutable=True)
        data.update(self.POST)
        address_form = AddressCreateForm(data=data)
        taxpayer_form = TaxPayerCreateForm(data=data)
        bankaccount_form = BankAccountCreateForm(data=data)
        self.assertEqual(6, len(address_form.data))
        self.assertEqual(8, len(taxpayer_form.data))
        self.assertEqual(4, len(bankaccount_form.data))


class TestEditTaxPayerInfo(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.taxpayer = TaxPayerArgentinaFactory()

        self.TAXPAYER_POST = {
            'csrfmiddlewaretoken': '67lLxnP0Q0oDIYThiF0z7cEcuLrmJSvT1OJUH0J9RyByLxiMeghEHuGKowoq4bZa',
            'taxpayer_form-workday_id': '1',
            'taxpayer_form-business_name': 'EB ARG',
            'taxpayer_form-cuit': '20-3123214-0',
            'taxpayer_form-country': 'AR',
            'taxpayer_form-comments': 'dafsadsffasdf',
            'taxpayer_form-payment_type': 'dafsadsffasdf',
        }
        self.POST = {
            'address_form-street': 'San Martin',
            'address_form-number': '21312',
            'address_form-zip_code': '123',
            'address_form-city': 'Mendoza',
            'address_form-state': 'Mendoza',
            'address_form-country': 'Argentina',
            'bankaccount_form-bank_name': 'Galicia',
            'bankaccount_form-bank_code': 'Cta Cte',
            'bankaccount_form-bank_account_number': '123214',
        }
        self.kwargs = {
            'taxpayer_id': self.taxpayer.id,
        }
        self.taxpayer_id = self.taxpayer.id

    def test_get_success_url_should_redirect_to_details_view(self):
        request = self.factory.get(
            '/suppliersite/ap/taxpayer/{}/update/taxpayer_info/'.format(self.taxpayer_id),
        )
        response = EditTaxpayerView.as_view()(request, **self.kwargs)
        self.assertEqual('AP_app/edit-taxpayer-information.html', response.template_name[0])

    def test_post_edit_taxpayer_info(self):
        request = self.factory.post(
            '/suppliersite/ap/taxpayer/{}/update/taxpayer_info/'.format(self.taxpayer_id),
            data=self.TAXPAYER_POST
        )
        response = EditTaxpayerView.as_view()(request, **self.kwargs)

        self.assertEqual('/suppliersite/ap/taxpayer/{}/details/'.format(self.taxpayer_id), response.url)


class TestEditAddressInfo(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.taxpayer = TaxPayerArgentinaFactory()
        self.address = AddressFactory(taxpayer=self.taxpayer)

        self.ADDRESS_POST = {
            'csrfmiddlewaretoken': '67lLxnP0Q0oDIYThiF0z7cEcuLrmJSvT1OJUH0J9RyByLxiMeghEHuGKowoq4bZa',
            'address_form-street': 'San Martin',
            'address_form-number': '21312',
            'address_form-zip_code': '123',
            'address_form-city': 'Mendoza',
            'address_form-state': 'Mendoza',
            'address_form-country': 'Argentina',
        }
        self.kwargs = {
            'taxpayer_id': self.taxpayer.id,
        }
        self.taxpayer_id = self.taxpayer.id

    def test_get_success_url_should_redirect_to(self):
        request = self.factory.get(
            '/suppliersite/ap/taxpayer/{}/update/address_info/'.format(self.taxpayer_id),
        )
        response = EditAddressView.as_view()(request, **self.kwargs)
        self.assertEqual('AP_app/edit-address-information.html', response.template_name[0])

    def test_post_edit_address_info(self):
        request = self.factory.post(
            '/suppliersite/ap/taxpayer/{}/update/address_info/'.format(self.taxpayer_id),
            data=self.ADDRESS_POST
        )
        response = EditAddressView.as_view()(request, **self.kwargs)

        self.assertEqual('/suppliersite/ap/taxpayer/{}/details/'.format(self.taxpayer_id), response.url)


class TestEditBankAccountInfo(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.taxpayer = TaxPayerArgentinaFactory()
        self.bank_account = BankAccountFactory(taxpayer=self.taxpayer)

        self.BANK_ACCOUNT_POST = {
            'csrfmiddlewaretoken': '67lLxnP0Q0oDIYThiF0z7cEcuLrmJSvT1OJUH0J9RyByLxiMeghEHuGKowoq4bZa',
            'bankaccount_form-bank_name': 'Galicia',
            'bankaccount_form-bank_code': 'Cta Cte',
            'bankaccount_form-bank_account_number': '123214',
        }

        self.kwargs = {
            'taxpayer_id': self.taxpayer.id,
        }
        self.taxpayer_id = self.taxpayer.id

    def test_get_success_url_should_redirect_to_details(self):
        request = self.factory.get(
            '/suppliersite/ap/taxpayer/{}/update/bank_account_info/'.format(self.taxpayer_id),
        )
        response = EditBankAccountView.as_view()(request, **self.kwargs)
        self.assertEqual('AP_app/edit-bank-account-information.html', response.template_name[0])

    def test_post_edit_bank_account_info(self):
        request = self.factory.post(
            '/suppliersite/ap/taxpayer/{}/update/bank_account_info/'.format(self.taxpayer_id),
            data=self.BANK_ACCOUNT_POST
        )
        response = EditBankAccountView.as_view()(request, **self.kwargs)

        self.assertEqual('/suppliersite/ap/taxpayer/{}/details/'.format(self.taxpayer_id), response.url)
