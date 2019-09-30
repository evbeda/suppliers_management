from os import (
    path,
    remove
)
from unittest.mock import MagicMock
from datetime import datetime
from pytz import UTC
from django.core.files import File
from django.test import Client, TestCase
from django.urls import reverse

from invoices_app.forms import InvoiceForm
from invoices_app.models import InvoiceArg
from users_app.models import User
from supplier_app.models import (
    Company,
    TaxPayer,

)


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


class TestApViews(TestCase):

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
            'invoice_file':self.file_mock
        }
        self.invoice_creation_empty_data = {}
        self.client = Client()
    
    def tearDown(self):
        if path.exists(self.file_mock.name):
            remove(self.file_mock.name)

    def test_ap_invoices_list_view(self):
        self.client.force_login(self.user)
        invoice = InvoiceArg.objects.create(**self.invoice_creation_valid_data)
        response = self.client.get(
            reverse('invoices-list')
        )
        self.assertContains(response, invoice.po_number)
        self.assertContains(response, invoice.taxpayer.name)

    def test_ap_invoices_list_are_in_new_status(self):
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
        invoice2.status = 'APPROVED'
        invoice2.save()

        response = self.client.get(
            reverse('invoices-list')
        )
        # Only the invoice with NEW status should be listed.
        self.assertContains(response, invoice1.taxpayer.name)
        self.assertNotContains(response, invoice2.taxpayer.name)


class TestAP(TestCase):
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
            'invoice_file':self.file_mock
        }
        self.invoice_creation_empty_data = {}
        self.client = Client()

    def tearDown(self):
        if path.exists(self.file_mock.name):
            remove(self.file_mock.name)

    def test_ap_invoices_list_view(self):
        self.client.force_login(self.user)
        invoice = InvoiceArg.objects.create(**self.invoice_creation_valid_data)
        response = self.client.get(
            reverse('invoices-list')
        )
        self.assertContains(response, invoice.po_number)
        self.assertContains(response, invoice.taxpayer.name)

    def test_ap_invoices_list_are_in_new_status(self):
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
        invoice2.status = 'APPROVED'
        invoice2.save()

        response = self.client.get(
            reverse('invoices-list')
        )
        # Only the invoice with NEW status should be listed.
        self.assertContains(response, invoice1.taxpayer.name)
        self.assertNotContains(response, invoice2.taxpayer.name)
