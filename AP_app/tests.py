from datetime import datetime
from http import HTTPStatus
from parameterized import parameterized
from pytz import UTC

from django.test import Client, TestCase
from django.urls import reverse

from users_app.models import User
from invoices_app.models import (
    Company,
    InvoiceArg,
    TaxPayer,
    TaxPayerState,
)


class TestAP(TestCase):
    def setUp(self):
        self.state = TaxPayerState()
        self.state.save()
        self.company = Company.objects.create(name='Company testing')
        self.user = User.objects.create_user(email='ap@eventbrite.com')
        self.tax_payer = TaxPayer(
            name='Eventbrite',
            workday_id='12345',
            tax_payer_state=self.state,
            company=self.company,
        )
        self.tax_payer.save()
        self.invoice_creation_valid_data = {
            'invoice_date': datetime(2007, 12, 5, 0, 0, 0, 0, UTC),
            'invoice_type': 'A',
            'invoice_number': '1234',
            'po_number': '98876',
            'currency': 'ARS',
            'net_amount': '4000',
            'vat': '1200',
            'total_amount': '5200',
            'tax_payer': self.tax_payer,
            'user': self.user,
        }
        self.invoice_creation_empty_data = {}
        self.client = Client()

    @parameterized.expand([
        ('ap-home',),
        ('ap-invoices',),
    ])
    def test_ap_site_permission(self, page_name):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse(page_name),
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @parameterized.expand([
        ('ap-home',),
        ('ap-invoices',),
    ])
    def test_ap_site_access_denied(self, page_name):
        user = User.objects.create_user(email='not_allowed@user.com')
        self.client.force_login(user)
        response = self.client.get(
            reverse(page_name),
            follow=True,
        )
        self.assertIn(('/login-error?next='+reverse(page_name), 302), response.redirect_chain)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.template_name, ['registration/invalid_login.html'])

    def test_ap_invoices_list_view(self):
        self.client.force_login(self.user)
        invoice = InvoiceArg.objects.create(**self.invoice_creation_valid_data)
        response = self.client.get(
            reverse('ap-invoices')
        )
        self.assertContains(response, invoice.tax_payer.name)
        self.assertContains(response, invoice.po_number)
