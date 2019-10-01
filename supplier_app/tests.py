from os import (
    path,
    remove
)
from parameterized import parameterized
from unittest import mock
from unittest.mock import patch

from django.http import HttpResponseRedirect, QueryDict
from django.test import TestCase, RequestFactory
from django.test import Client
from django.core.files import File as DjangoFile
from django.core.urlresolvers import (
    resolve,
    reverse,
)

from supplier_app.forms import (
    PDFFileForm,
    AddressCreateForm,
    BankAccountCreateForm,
    TaxPayerCreateForm,
)

from supplier_app.views import (
    CreateTaxPayerView,
    SupplierHome,
    ApTaxpayers,
)

from users_app.models import User
from social_django.models import UserSocialAuth
from supplier_app.models import (
    Company,
    TaxPayer,
    TaxPayerArgentina,
    BankAccount,
    Address,
    CompanyUserPermission,
    PDFFile,
)

GENERIC_PASSWORD = '1234'
POST = {
            'csrfmiddlewaretoken': '67lLxnP0Q0oDIYThiF0z7cEcuLrmJSvT1OJUH0J9RyByLxiMeghEHuGKowoq4bZa',
            'taxpayer_form-workday_id': '1',
            'taxpayer_form-name': 'EB ARG',
            'taxpayer_form-razon_social': 'Monotributista',
            'taxpayer_form-cuit': '20-3123214-0',
            'taxpayer_form-country': 'AR',
            'taxpayer_form-justificacion': 'dafsadsffasdf',
            'taxpayer_form-forma_de_pago': 'dafsadsffasdf',
            'address_form-street': 'San Martin',
            'address_form-number': '21312',
            'address_form-zip_code': '123',
            'address_form-city': 'Mendoza',
            'address_form-state': 'Mendoza',
            'address_form-country': 'Argentina',
            'bankaccount_form-bank_name': 'Ganicia',
            'bankaccount_form-bank_code': 'Cta Cte',
            'bankaccount_form-account_number': '123214',
}


class TestModels(TestCase):
    def setUp(self):
        self.taxpayer = {
            'name': 'Eventbrite',
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
            'name': 'Eventbrite',
            'workday_id': '12345',
            'razon_social': 'Sociedad Anonima',
            'cuit': '20-31789965-3'
        }
        self.taxpayer_ar2 = {
            'name': 'Cocacola',
            'workday_id': '67890',
            'taxpayer_state': 'PENDING',
            'razon_social': 'Sociedad Anonima',
            'cuit': '30-31789965-5'
        }

    def test_company(self):
        company = Company(**self.company)
        self.assertEqual(company.name, self.company['name'])
        self.assertEqual(company.description, self.company['description'])
        self.assertEqual(
            str(company),
            "Company:{}".format(
                self.company['name']
            )
        )

    def test_company_user_permissions(self):
        user = User.objects.create(**self.user)
        company = Company.objects.create(**self.company)
        company_user_permissions = \
            CompanyUserPermission.objects.create(user=user, company=company)
        self.assertEqual(
            company_user_permissions.user.email,
            self.user['email']
        )
        self.assertEqual(
            company_user_permissions.company.name,
            self.company['name']
        )

    def test_company_of_tax_payer(self):
        company = Company.objects.create(**self.company)
        taxpayer1 = TaxPayer.objects.create(**self.taxpayer, company=company)
        self.assertEqual(taxpayer1.company.name, "Eventbrite")

    def test_tax_payer_entity(self):
        company = Company.objects.create(**self.company)
        taxpayer = TaxPayer.objects.create(**self.taxpayer, company=company)
        self.assertEqual(taxpayer.name, 'Eventbrite')
        self.assertEqual(taxpayer.workday_id, '12345')

    def test_state_when_create_tax_payer_first_time(self):
        company = Company.objects.create(**self.company)
        taxpayer = TaxPayer.objects.create(**self.taxpayer, company=company)
        self.assertEqual(taxpayer.taxpayer_state, "PENDING")
        self.assertEqual(str(taxpayer), "Name:Eventbrite Status:PENDING")

    def test_create_child_of_tax_payer(self):
        taxpayer_ar1 = TaxPayerArgentina(**self.taxpayer_ar1)
        self.assertTrue(isinstance(taxpayer_ar1, TaxPayer))
        self.assertEqual(taxpayer_ar1.name, 'Eventbrite')
        self.assertEqual(
            str(taxpayer_ar1),
            "Name:Eventbrite Status:PENDING"
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
            account_number='44-2417027-3',
            taxpayer=taxpayer1
        )
        self.assertEqual(bank.taxpayer.name, 'Eventbrite')
        self.assertEqual(str(bank), "Bank:{} bank_code:{} account_number:{}".format(
            'Supervielle',
            'CA $',
            '44-2417027-3',
        ))

    def test_get_taxpayer_childs(self):

        company = Company.objects.create(**self.company)
        TaxPayerArgentina.objects.create(**self.taxpayer_ar1, company=company)
        TaxPayerArgentina.objects.create(**self.taxpayer_ar2, company=company)
        taxpayers = TaxPayer.get_taxpayer_childs()
        self.assertEqual(
            str(taxpayers),
            '[<TaxPayerArgentina: Name:Eventbrite Status:PENDING>, <TaxPayerArgentina: Name:Cocacola Status:PENDING>]'
        )
    
    def test_get_taxpayer_child(self):
        company = Company.objects.create(**self.company)
        taxpayerar = TaxPayerArgentina.objects.create(**self.taxpayer_ar1, company=company)
        self.assertEqual(
            str(taxpayerar.get_taxpayer_child()),
            'Name:Eventbrite Status:PENDING'
        )


class TestCreateTaxPayer(TestCase):
    def setUp(self):
        self.client = Client()
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
        self.factory = RequestFactory()

    def _get_example_forms(self):
        FORM_POST = QueryDict('', mutable=True)
        FORM_POST.update(POST)
        forms = {
            'address_form': AddressCreateForm(FORM_POST),
            'bankaccount_form': BankAccountCreateForm(FORM_POST),
            'taxpayer_form': TaxPayerCreateForm(self.user_with_eb_social, FORM_POST)
        }
        return forms

    def test_get_success_url_should_redirect_to_home(self):
        self.assertEqual(
            '/suppliersite/supplier', self.create_taxpayer_view.get_success_url()
            )

    def test_GET_taxpayer_view_should_render_3_forms(self):
        response = self.client.get('/suppliersite/supplier/taxpayer/create')
        taxpayer_form = response.context_data['taxpayer_form']
        address_form = response.context_data['address_form']
        bankaccount_form = response.context_data['bankaccount_form']
        self.assertEqual(AddressCreateForm, type(address_form))
        self.assertEqual(BankAccountCreateForm, type(bankaccount_form))
        self.assertEqual(TaxPayerCreateForm, type(taxpayer_form))

    def test_valid_forms_pass_validation(self):
        forms = self._get_example_forms()
        self.assertTrue(self.create_taxpayer_view.forms_are_valid(forms))

    @patch(
        'supplier_app.views.CreateTaxPayerView.form_valid',
        return_value=HttpResponseRedirect('/suppliersite/supplier')
        )
    def test_form_valid_method_should_be_called_with_an_valid_POST(self, mocked_valid_form):
        self.client.post('/suppliersite/supplier/taxpayer/create', POST)
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
        request = self.factory.get('/suppliersite/home')
        request.user = self.user_with_eb_social
        self.create_taxpayer_view.request = request
        self.create_taxpayer_view.form_valid(forms)
        taxpayer = TaxPayerArgentina.objects.filter(name='EB ARG')
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
        self.assertEquals(response.status_code, 302)


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
        #self.taxpayer = TaxPayer.objects.create(name='Eventbrite', workday_id='12345', company=self.company)
        self.taxpayer_ar = TaxPayerArgentina.objects.create(
            name='Eventbrite',
            workday_id='12345',
            taxpayer_state='PENDING',
            razon_social='Sociedad Anonima',
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
            name='Pyme 1',
            workday_id='1',
            taxpayer_state='PENDING',
            razon_social='Empresa 1 Sociedad Anonima',
            cuit='20-31789965-3',
            company=self.company1,
        )
        self.taxpayer_ar2 = TaxPayerArgentina.objects.create(
            name='Pyme 2',
            workday_id='2',
            taxpayer_state='CHANGE REQUIRED',
            razon_social='Empresa 2 Sociedad Responsabilidad Limitada',
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

        self.assertEqual(response.status_code, 200)