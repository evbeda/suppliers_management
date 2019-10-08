from os import (
    path,
)
from parameterized import parameterized
from shutil import rmtree
from unittest.mock import (
    MagicMock,
    patch,
)

from django.core.files import File
from django.http import (
    HttpResponseRedirect,
    QueryDict
)
from django.test import (
    Client,
    RequestFactory,
    TestCase,
)
from django.utils.datastructures import MultiValueDict


from supplier_app.tests.factory_boy import (
    CompanyFactory,
    CompanyUserPermissionFactory,
)
from supplier_app.forms import (
    AddressCreateForm,
    BankAccountCreateForm,
    BasePrefixCreateForm,
    TaxPayerCreateForm,
)

from supplier_app.views import (
    CreateTaxPayerView,
)

from users_app.factory_boy import UserFactory


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


class TestTaxPayerFormValidation(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50
        self.create_taxpayer_view = CreateTaxPayerView()
        self.company = CompanyFactory()
        self.user_with_eb_social = UserFactory()
        self.client.force_login(self.user_with_eb_social)
        self.companyuserpermission = CompanyUserPermissionFactory(
            company=self.company,
            user=self.user_with_eb_social
        )
        self.POST = {
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
        AFIP_file=None,
        witholding_taxes_file=None,
        bank_cbu_file=None
    ):
        return MultiValueDict({
            'taxpayer_form-AFIP_registration_file': [
                AFIP_file or self.file_mock
            ],
            'taxpayer_form-witholding_taxes_file': [
                witholding_taxes_file or self.file_mock
            ],
            'bankaccount_form-bank_cbu_file': [
                bank_cbu_file or self.file_mock
            ],
        })

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
    ])
    def test_form_with_a_file_greater_than_25MB_should_be_invalid(
        self,
        param_size,
        attr
    ):
        request = self.factory.post(
            '/suppliersite/supplier/taxpayer/create',
            data=self.POST
        )
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
    ])
    def test_form_with_a_non_PDF_type_file_should_be_invalid(
        self,
        param_name,
        attr
    ):
        request = self.factory.post(
            'suppliersite/supplier/taxpayer/create',
            data=self.POST
        )
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
    def test_form_valid_method_should_be_called_with_an_valid_POST(
        self,
        mocked_valid_form
    ):
        request = self.factory.post(
            '/suppliersite/supplier/taxpayer/create',
            data=self.POST
        )
        request.user = self.user_with_eb_social
        request.FILES.update(self._get_request_FILES())
        CreateTaxPayerView.as_view()(request)
        mocked_valid_form.assert_called()

    @patch(
        'supplier_app.views.CreateTaxPayerView.form_invalid',
        return_value=HttpResponseRedirect('/suppliersite/supplier')
        )
    def test_form_invalid_method_should_be_called_with_an_invalid_POST(
        self,
        mocked_invalid_form
    ):
        self.client.post(
            '/suppliersite/supplier/taxpayer/create',
            {'asda': 'asd'}
        )
        mocked_invalid_form.assert_called()