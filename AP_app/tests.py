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
)


class TestAP(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Company testing')
        self.user = User.objects.create_user(email='ap@eventbrite.com')
        self.taxpayer = TaxPayer.objects.create(
            name='Eventbrite',
            workday_id='12345',
            company=self.company,
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
            'taxpayer': self.taxpayer,
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
        # self.assertContains(response, invoice.taxpayer.name)
        self.assertContains(response, invoice.po_number)
