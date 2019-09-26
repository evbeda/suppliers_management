from os import (
    path,
    remove
)
from unittest.mock import patch
from unittest.mock import MagicMock
from unittest import mock
from parameterized import parameterized

from datetime import datetime
from pytz import UTC

from .forms import InvoiceForm

from django.core.files import File
from django.http import QueryDict


from django.test import TestCase
from django.test import Client
from django.http import HttpResponseRedirect
from django.core.files import File as DjangoFile
from django.core.urlresolvers import (
    resolve,
    reverse,
)

from .models import PDFFile
from .forms import PDFFileForm

from .views import (
    CreateTaxPayerView,
    AddressCreateForm,
    BankAccountCreateForm,
    TaxPayerCreateForm,
)

from users_app.models import User
from social_django.models import UserSocialAuth
from invoices_app.models import (
    Company,
    TaxPayer,
    TaxPayerArgentina,
    BankAccount,
    Address,
    InvoiceArg,
    CompanyUserPermission
)


GENERIC_PASSWORD = '1234'
POST = {
            'csrfmiddlewaretoken': '67lLxnP0Q0oDIYThiF0z7cEcuLrmJSvT1OJUH0J9RyByLxiMeghEHuGKowoq4bZa',
            'taxpayer_form-workday_id': '1',
            'taxpayer_form-name': 'EB ARG',
            'taxpayer_form-company': '1',
            'taxpayer_form-razon_social': 'Monotributista',
            'taxpayer_form-cuit': '20-3123214-0',
            'address_form-street': 'San Martin',
            'address_form-number': '21312',
            'address_form-zip_code': '123',
            'address_form-city': 'Mendoza',
            'address_form-state': 'Mendoza',
            'address_form-country': 'Argentina',
            'bankaccount_form-bank_name': 'Ganicia',
            'bankaccount_form-account_type': 'Cta Cte',
            'bankaccount_form-account_number': '123214',
            'bankaccount_form-identifier': '12312512'
}


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
            '/suppliersite/home', self.create_taxpayer_view.get_success_url()
            )

    def test_user_with_1_company_should_only_select_his_1_company(self):
        taxpayer_form = TaxPayerCreateForm(self.user_with_eb_social)
        self.assertEqual(1, len(taxpayer_form.get_user_companies(self.user_with_eb_social)))

    def test_GET_taxpayer_view_should_render_3_forms(self):
        response = self.client.get('/suppliersite/taxpayer/create')
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
        return_value=HttpResponseRedirect('/suppliersite/home')
        )
    def test_form_valid_method_should_be_called_with_an_valid_POST(self, mocked_valid_form):
        self.client.post('/suppliersite/taxpayer/create', POST)
        mocked_valid_form.assert_called()

    @patch(
        'supplier_app.views.CreateTaxPayerView.form_invalid',
        return_value=HttpResponseRedirect('/suppliersite/home')
        )
    def test_form_invalid_method_should_be_called_with_an_invalid_POST(self, mocked_invalid_form):
        self.client.post('/suppliersite/taxpayer/create', {
            'asda': 'asd',
        })
        mocked_invalid_form.assert_called()

    def test_form_valid_method_should_save_taxpayer_address_bankaccount(self):
        forms = self._get_example_forms()
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
        self.create_taxpayer_view.form_valid(forms)
        address = Address.objects.get(street='San Martin')
        bankaccount = BankAccount.objects.get(bank_name='Ganicia')
        self.assertEqual('Name:EB ARG Status:PEND', str(address.taxpayer))
        self.assertEqual('Name:EB ARG Status:PEND', str(bankaccount.taxpayer))


class TestInvoice(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Company testing')
        self.user = User.objects.create_user(email='test_test@test.com')
        self.taxpayer = TaxPayer.objects.create(
            name='Eventbrite',
            workday_id='12345',
            company=self.company
        )
        self.invoice_creation_valid_data = {
            'invoice_date': datetime(2007, 12, 5, 0, 0, 0, 0, UTC),
            'invoice_type': 'A',
            'invoice_number': '1234',
            'po_number': '98876',
            'currency': 'ARS',
            'net_amount': '4000',
            'vat': '1200',
            'total_amount': '5200',
            'invoice_file': 'test.pdf',
            'taxpayer': self.taxpayer,
            'user': self.user,
        }
        self.invoice_creation_empty_data = {}
        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50

    def tearDown(self):
        if path.exists(self.file_mock.name):
            remove(self.file_mock.name)

    def test_invoice_create(self):
        form = InvoiceForm(
            data=self.invoice_creation_valid_data,
            files={
                'invoice_file': self.file_mock,
            }
        )
        self.assertTrue(form.is_valid())

    def test_invoice_create_required_fields(self):
        form = InvoiceForm(
            data=self.invoice_creation_empty_data
        )
        self.assertFalse(form.is_valid())

    def test_invoice_create_db(self):
        invoice = InvoiceArg.objects.create(
            invoice_date=datetime(2007, 12, 5, 0, 0, 0, 0, UTC),
            taxpayer=self.taxpayer,
            invoice_type='A',
            invoice_number='1234',
            po_number='98876',
            currency='ARS',
            net_amount='4000',
            vat='1200',
            total_amount='5200',
            invoice_file=self.file_mock,
            user=self.user,
            )
        self.assertEqual(
            InvoiceArg.objects.get(invoice_number='1234'), invoice
            )

    def test_supplier_invoices_list_view(self):
        self.client.force_login(self.user)
        invoice = InvoiceArg.objects.create(
            invoice_date=datetime(2007, 12, 5, 0, 0, 0, 0, UTC),
            taxpayer=self.taxpayer,
            invoice_type='A',
            invoice_number='1234',
            po_number='98876',
            currency='ARS',
            net_amount='4000',
            vat='1200',
            total_amount='5200',
            user=self.user,
            invoice_file=self.file_mock
        )
        response = self.client.get(
            reverse('supplier-invoice-list', kwargs={'taxpayer_id': self.taxpayer.id}),
        )
        self.assertContains(response, invoice.po_number)
        self.assertContains(response, invoice.status)

    def test_supplier_invoices_list_only_taxpayer_invoices(self):
        self.client.force_login(self.user)
        invoice1 = InvoiceArg.objects.create(**self.invoice_creation_valid_data)

        other_tax_payer = TaxPayer.objects.create(
            name='Test Tax Payer',
            workday_id='12345',
            company=self.company,
        )
        other_invoice_data = self.invoice_creation_valid_data
        other_invoice_data['taxpayer'] = other_tax_payer
        invoice2 = InvoiceArg.objects.create(**other_invoice_data)

        response = self.client.get(
            reverse('supplier-invoice-list', kwargs={'taxpayer_id': self.taxpayer.id}),
        )
        # Only the invoice with from the tax payer should be listed.
        self.assertIn(
            invoice1.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertNotIn(
            invoice2.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )


    def test_supplier_invoices_list_404_if_invalid_supplier(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('supplier-invoice-list', kwargs={'taxpayer_id': 999}),
        )
        self.assertEqual(response.status_code, 404)


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
