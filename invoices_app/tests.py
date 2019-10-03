from os import (
    path,
    remove
)
from parameterized import parameterized
from unittest.mock import MagicMock
from datetime import datetime
from pytz import UTC
from http import HTTPStatus

from django.core.files import File
from django.test import (
    Client,
    TestCase
)
from django.urls import reverse
from django.http import HttpResponseRedirect

from invoices_app.factory_boy import InvoiceFactory
from supplier_app.factory_boy import (
    TaxPayerArgentinaFactory,
    CompanyFactory,
    AddressFactory,
)
from invoices_app.views import invoice_history_changes
from users_app.factory_boy import UserFactory

from invoices_app.forms import InvoiceForm
from invoices_app.models import Invoice
from users_app.models import User
from supplier_app.models import (
    Company,
    TaxPayer,
    CompanyUserPermission
)
from invoices_app import (
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_NEW,
    INVOICE_STATUS_REJECTED,
)


class TestBase(TestCase):
    def invoice_creation(self, taxpayer=None, user=None):
        if not taxpayer:
            taxpayer = self.taxpayer

        if not user:
            user = self.user

        return {
            'invoice_date': datetime(2007, 12, 5, 0, 0, 0, 0, UTC),
            'invoice_type': 'A',
            'invoice_number': '1234',
            'po_number': '98876',
            'currency': 'ARS',
            'net_amount': '4000',
            'vat': '1200',
            'total_amount': '5200',
            'invoice_file': 'test.pdf',
            'taxpayer': taxpayer,
            'user': user,
        }

    def setUp(self):
        self.company = CompanyFactory()
        self.ap_user = User.objects.create_user(email='ap@eventbrite.com')
        self.user = UserFactory()
        self.taxpayer = TaxPayerArgentinaFactory(company=self.company)
        self.address = AddressFactory(taxpayer=self.taxpayer)
        self.user2 = UserFactory()
        self.taxpayer1_user2 = TaxPayerArgentinaFactory(company=self.company)
        self.invoice_creation_valid_data = self.invoice_creation()
        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50
        self.invoice_edit_data = {
            'invoice_date': '2019-10-01',
            'invoice_type': 'A',
            'invoice_number': '987654321',
            'po_number': '98876',
            'currency': 'ARS',
            'net_amount': '4000',
            'vat': '1200',
            'total_amount': '5200',
            'taxpayer': self.taxpayer.id,
            'user': self.user.id,
            'invoice_file': self.file_mock,
        }
        self.invoice_creation_empty_data = {}
        self.invoice_post_data = {
                'invoice_date': '2019-10-01',
                'invoice_type': 'A',
                'invoice_number': '987654321',
                'po_number': '98876',
                'currency': 'ARS',
                'net_amount': '4000',
                'vat': '1200',
                'total_amount': '5200',
                'taxpayer': self.taxpayer.id,
                'user': self.user.id,
                'invoice_file': self.file_mock,
            }
        self.client = Client()

    def tearDown(self):
        if self.file_mock and path.exists('file/{}'.format(self.file_mock.name)):
            remove('file/{}'.format(self.file_mock.name))


class TestInvoice(TestBase):

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

    @parameterized.expand([
        ('test.pdf', 20, True),
        ('test.xml', 20, False),
        ('test.pdf', 500000000, False),
        ('test.xml', 500000000, False),

    ])
    def test_form_file_is_valid(self, name_file, size_file, expected):
        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = name_file
        self.file_mock.size = size_file
        form = InvoiceForm(
            data=self.invoice_post_data,
            files={
                'invoice_file': self.file_mock,
            }
        )
        self.assertEqual(form.is_valid(), expected)

    def test_invoice_create_db(self):
        invoice = Invoice.objects.create(
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
            Invoice.objects.get(invoice_number='1234'), invoice
            )

    def test_invoice_create_view(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('invoice-create', kwargs={'taxpayer_id': self.taxpayer.id}),
            self.invoice_post_data,
        )
        self.assertEqual(response.status_code, 302)
        invoice = Invoice.objects.get(invoice_number=self.invoice_post_data['invoice_number'])
        self.assertEqual(invoice.status, INVOICE_STATUS_NEW)

    def test_invoice_create_existing_invoice_id(self):
        self.client.force_login(self.user)
        invoice = Invoice.objects.create(**self.invoice_creation_valid_data)
        self.invoice_post_data['invoice_number'] = invoice.invoice_number
        response = self.client.post(
            reverse('invoice-create', kwargs={'taxpayer_id': self.taxpayer.id}),
            self.invoice_post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The invoice {} already exists'.format(invoice.invoice_number))

    def test_supplier_invoices_list_view(self):
        self.client.force_login(self.user)
        invoice = Invoice.objects.create(
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
            invoice_file=self.file_mock,
        )
        response = self.client.get(
            reverse('supplier-invoice-list', kwargs={'taxpayer_id': self.taxpayer.id}),
        )
        self.assertContains(response, invoice.po_number)
        self.assertContains(response, invoice.status)

    def test_supplier_invoices_list_only_taxpayer_invoices(self):
        self.client.force_login(self.user)
        invoice1 = InvoiceFactory(
            user=self.user,
            taxpayer=self.taxpayer
        )

        other_tax_payer = TaxPayerArgentinaFactory(company=self.company)
        invoice2 = InvoiceFactory(
            user=self.user,
            taxpayer=other_tax_payer
        )

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

    def test_supplier_with_two_invoices_list_only_two_invoices(self):
        self.client.force_login(self.user2)

        invoice1 = InvoiceFactory(user=self.user2, taxpayer=self.taxpayer1_user2, invoice_number=1234)
        invoice2 = InvoiceFactory(user=self.user2, taxpayer=self.taxpayer1_user2, invoice_number=1235)

        response = self.client.get(
            reverse('invoices-list')
        )
        # Only the invoice with from the tax payer should be listed.
        self.assertIn(
            invoice1.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertIn(
            invoice2.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertEqual(2, len(response.context_data['object_list']))

    def test_AP_should_see_all_invoices(self):
        self.client.force_login(self.ap_user)

        invoice1_user1 = InvoiceFactory(user=self.user, taxpayer=self.taxpayer, invoice_number=1234)
        invoice2_user1 = InvoiceFactory(user=self.user, taxpayer=self.taxpayer, invoice_number=1235)
        invoice1_user2 = InvoiceFactory(user=self.user2, taxpayer=self.taxpayer1_user2, invoice_number=1236)
        invoice2_user2 = InvoiceFactory(user=self.user2, taxpayer=self.taxpayer1_user2, invoice_number=1237)
        response = self.client.get(
            reverse('invoices-list')
        )
        # Only the invoice with from the tax payer should be listed.
        self.assertIn(
            invoice1_user1.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertIn(
            invoice1_user2.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertIn(
            invoice2_user1.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertIn(
            invoice2_user2.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertEqual(4, len(response.context_data['object_list']))

    def test_supplier_invoices_list_404_if_invalid_supplier(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('supplier-invoice-list', kwargs={'taxpayer_id': 999}),
        )
        self.assertEqual(response.status_code, 404)

    @parameterized.expand([
        ('invoice-approve', 1, 302),
        ('invoice-approve', 31, 404),
        ('invoice-reject', 1, 302),
        ('invoice-reject', 31, 404),
    ])
    def test_invoice_change_status(self, url, invoice_id, expected):
        self.client.force_login(self.ap_user)
        Invoice.objects.create(**self.invoice_creation_valid_data)
        response = self.client.get(
            reverse(url, kwargs={'pk': invoice_id}),
        )
        self.assertEqual(response.status_code, expected)

    @parameterized.expand([
        ('invoice-approve', INVOICE_STATUS_APPROVED),
        ('invoice-reject', INVOICE_STATUS_REJECTED),
    ])
    def test_invoice_change_status_changed(self, url, expected):
        self.client.force_login(self.ap_user)
        invoice = Invoice.objects.create(**self.invoice_creation_valid_data)
        self.client.get(
            reverse(url, kwargs={'pk': 1}),
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, expected)

    def test_invoice_change_status_only_ap_fail(self):
        self.client.force_login(self.user)
        Invoice.objects.create(**self.invoice_creation_valid_data)
        request = self.client.get(
            reverse('invoice-approve', kwargs={'pk': 1}),
        )
        self.assertEqual(request.status_code, 403)

    def test_supplier_invoice_edit(self):
        self.client.force_login(self.user)
        invoice = Invoice.objects.create(**self.invoice_creation_valid_data)
        invoice.status = 'CHANGES REQUEST'
        invoice.save()
        res = self.client.post(
            reverse('taxpayer-invoice-update', kwargs={'taxpayer_id': self.taxpayer.id, 'pk': invoice.id}),
            self.invoice_post_data
        )
        self.assertEqual(res.status_code, 302)
        invoice.refresh_from_db()
        self.assertEqual(invoice.invoice_number, self.invoice_post_data['invoice_number'])

    def test_supplier_invalid_invoice_edit_request(self):
        self.client.force_login(self.user)
        invoice = Invoice.objects.create(**self.invoice_creation_valid_data)
        invoice.status = 'CHANGES REQUEST'
        invoice.save()
        old_invoice_number = invoice.invoice_number
        res = self.client.post(
            reverse('taxpayer-invoice-update', kwargs={'taxpayer_id': self.taxpayer.id, 'pk': invoice.id}),
            {}
        )
        self.assertEqual(res.status_code, 200)
        invoice.refresh_from_db()
        self.assertEqual(invoice.invoice_number, old_invoice_number)
        self.assertContains(res, 'This field is required.')

    def test_supplier_invoice_edit_permissions(self):
        self.client.force_login(self.user)
        invoice = Invoice.objects.create(**self.invoice_creation_valid_data)
        invoice.status = 'APPROVED'
        invoice.save()
        res = self.client.post(
            reverse('taxpayer-invoice-update', kwargs={'taxpayer_id': self.taxpayer.id, 'pk': invoice.id}),
            self.invoice_post_data,
            follow=True,
        )
        self.assertIn(
            (reverse('supplier-invoice-list', kwargs={'taxpayer_id': self.taxpayer.id}), 302),
            res.redirect_chain
        )
        self.assertEqual(res.status_code, 200)

    def test_ap_invoice_edit_permissions(self):
        self.client.force_login(self.ap_user)
        invoice = Invoice.objects.create(**self.invoice_creation_valid_data)
        invoice.status = 'APPROVED'
        invoice.save()
        res = self.client.post(
            reverse('taxpayer-invoice-update', kwargs={'taxpayer_id': self.taxpayer.id, 'pk': invoice.id}),
            self.invoice_post_data,
        )
        self.assertEqual(res.status_code, 302)
        invoice.refresh_from_db()
        self.assertEqual(invoice.invoice_number, self.invoice_post_data['invoice_number'])

    def test_invoice_create_get_context_data(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('invoice-create', kwargs={'taxpayer_id': self.taxpayer.id}))
        self.assertEqual(response.context['taxpayer_id'], str(self.taxpayer.id))


class TestApViews(TestBase):

    def test_ap_invoices_list_view(self):
        self.client.force_login(self.user)
        invoice = Invoice.objects.create(**self.invoice_creation_valid_data)
        response = self.client.get(
            reverse('invoices-list')
        )
        self.assertContains(response, invoice.po_number)
        self.assertContains(response, invoice.taxpayer.name)

    def test_ap_invoices_list_are_in_new_status(self):
        self.client.force_login(self.ap_user)
        invoice1 = Invoice.objects.create(**self.invoice_creation_valid_data)
        other_tax_payer = TaxPayer.objects.create(
            name='Test Tax Payer',
            workday_id='12345',
            company=self.company,
        )
        other_invoice_data = self.invoice_creation_valid_data
        other_invoice_data['taxpayer'] = other_tax_payer
        invoice2 = Invoice.objects.create(**other_invoice_data)
        invoice2.status = INVOICE_STATUS_APPROVED
        invoice2.save()

        response = self.client.get(
            reverse('invoices-list')
        )
        # Only the invoice with NEW status should be listed.
        self.assertContains(response, invoice1.taxpayer.name)
        self.assertNotContains(response, invoice2.taxpayer.name)


class TestAP(TestBase):

    def test_ap_invoices_list_view(self):
        self.client.force_login(self.ap_user)
        invoice = Invoice.objects.create(**self.invoice_creation_valid_data)
        response = self.client.get(
            reverse('invoices-list')
        )
        self.assertContains(response, invoice.po_number)
        self.assertContains(response, invoice.taxpayer.name)

    def test_ap_invoices_list_are_in_new_status(self):
        self.client.force_login(self.ap_user)
        invoice1 = Invoice.objects.create(**self.invoice_creation_valid_data)
        other_tax_payer = TaxPayer.objects.create(
            name='Test Tax Payer',
            workday_id='12345',
            company=self.company,
        )
        other_invoice_data = self.invoice_creation_valid_data
        other_invoice_data['taxpayer'] = other_tax_payer
        invoice2 = Invoice.objects.create(**other_invoice_data)
        invoice2.status = INVOICE_STATUS_APPROVED
        invoice2.save()

        response = self.client.get(
            reverse('invoices-list')
        )
        # Only the invoice with NEW status should be listed.
        self.assertContains(response, invoice1.taxpayer.name)
        self.assertNotContains(response, invoice2.taxpayer.name)


class DetailInvoiceTest(TestBase):

    def test_click_in_row_invoice_redirects_to_detail_invoice(self):
        self.client.force_login(self.user)
        invoice = Invoice.objects.create(
            **self.invoice_creation_valid_data
        )
        response = self.client.get(
            reverse('invoices-detail',
            kwargs={
                'taxpayer_id': invoice.taxpayer.id,
                'pk': invoice.id,
                }
            ),
        )
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual("/?next=/invoices/taxpayer/1/detail/1/", response.url)

    def test_get_detail_invoice_without_login(self):
        invoice = Invoice.objects.create(
            **self.invoice_creation_valid_data
        )
        response = self.client.get(
            reverse('invoices-detail',
            kwargs={
                'taxpayer_id': invoice.taxpayer.id,
                'pk': invoice.id,
                }
            ),
        )
        self.assertEqual(type(response), HttpResponseRedirect)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(response.url, "/?next=/invoices/taxpayer/1/detail/1/")

    def test_get_detail_invoice_with_no_corresponding_supplier(self):
        self.client.force_login(self.user)

        self.other_user = User.objects.create_user(email='other_test@test.com')
        self.other_company = Company.objects.create(name='Other Company testing')
        self.other_taxpayer = TaxPayer.objects.create(
            name='Other',
            workday_id='1234',
            company=self.other_company
        )
        self.companuuserpermission = CompanyUserPermission.objects.create(
            company=self.company,
            user=self.user
        )

        invoice_from_other_user = Invoice.objects.create(
            **self.invoice_creation(self.other_taxpayer, self.other_user)
        )

        response = self.client.get(
            reverse('invoices-detail',
            kwargs={
                'taxpayer_id': invoice_from_other_user.taxpayer.id,
                'pk': invoice_from_other_user.id,
                }
            ),
        )

        self.assertEqual(type(response), HttpResponseRedirect)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(response.url, "/?next=/invoices/taxpayer/3/detail/1/")
    
    def test_suplier_invoice_detail_view_address(self):
        self.client.force_login(self.user)
        CompanyUserPermission.objects.create(
            company=self.taxpayer.company,
            user=self.user
        )
        invoice = Invoice.objects.create(**self.invoice_creation_valid_data)
        response = self.client.get(reverse('invoices-detail', kwargs={'taxpayer_id': self.taxpayer.id,'pk': invoice.id}))
        self.assertEqual(response.context['address'], self.address)

    def test_ap_invoice_detail_view_address(self):
        self.client.force_login(self.ap_user)
        invoice = Invoice.objects.create(**self.invoice_creation_valid_data)
        response = self.client.get(reverse('invoices-detail', kwargs={'taxpayer_id': self.taxpayer.id,'pk': invoice.id}))
        self.assertEqual(response.context['address'],self.address)


class TestInvoiceHistory(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Company testing')
        self.user = User.objects.create_user(email='ap@eventbrite.com')
        self.taxpayer = TaxPayer.objects.create(
            name='Eventbrite',
            workday_id='12345',
            company=self.company,
        )
        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50
        self.invoice_creation_valid_data = {
            'invoice_date': datetime(2007, 12, 5, 0, 0, 0, 0, UTC),
            'invoice_type': 'A',
            'invoice_number': '1234',
            'po_number': '98876',
            'currency': 'ARS',
            'net_amount': '4000',
            'vat': '1200',
            'total_amount': '5200',
            'taxpayer': self.taxpayer,
            'user': self.user,
            'invoice_file': self.file_mock.name
        }

    def tearDown(self):
        if self.file_mock and path.exists('file/{}'.format(self.file_mock.name)):
            remove('file/{}'.format(self.file_mock.name))

    def test_history_changes_diff(self):
        invoice = Invoice.objects.create(**self.invoice_creation_valid_data)
        invoice.po_number = '4321'
        invoice.save()
        history = Invoice.history.filter(id=invoice.id)
        self.assertEqual(
            invoice_history_changes(history.last()),
            [{'field': 'po_number', 'old': '98876', 'new': '4321'}]
        )

    def test_history_invoices_view(self):
        invoice = Invoice.objects.create(**self.invoice_creation_valid_data)
        old_po_number = invoice.po_number
        new_po_number = '4321'
        invoice.po_number = new_po_number
        invoice.save()
        response = self.client.get(
            reverse('invoice-history', kwargs={'pk': invoice.id}),
        )
        self.assertContains(response, old_po_number)
        self.assertContains(response, new_po_number)
