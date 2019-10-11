from os import (
    path,
    remove
)
from unittest.mock import MagicMock

from django.core.files import File
from django.test import (
    Client,
    TestCase
)
from django.core import mail
from invoices_app.factory_boy import InvoiceFactory

from supplier_app.tests.factory_boy import (
    TaxPayerArgentinaFactory,
    CompanyFactory,
    CompanyUserPermissionFactory,
    AddressFactory
)

from users_app.factory_boy import UserFactory
from users_app.models import User


class TestBase(TestCase):

    def setUp(self):
        self.ap_user = User.objects.create_user(email='ap@eventbrite.com')

        self.user = UserFactory()
        self.company = CompanyFactory()
        self.taxpayer = TaxPayerArgentinaFactory(company=self.company)
        self.companyuserpermission = CompanyUserPermissionFactory(
            company=self.company,
            user=self.user
        )
        self.invoice = InvoiceFactory(
            user=self.user,
            taxpayer=self.taxpayer,
            invoice_number='1234'
        )
        self.address = AddressFactory(taxpayer=self.taxpayer)

        self.other_user = UserFactory()
        self.company_for_other_user = CompanyFactory()
        self.cup_for_other_user = CompanyUserPermissionFactory(
            company=self.company_for_other_user,
            user=self.other_user
        )
        self.taxpayer_for_other_user = TaxPayerArgentinaFactory(company=self.company_for_other_user)
        self.invoice_from_other_user = InvoiceFactory(
            user=self.other_user,
            taxpayer=self.taxpayer_for_other_user,
            invoice_number='1235'
        )

        self.user_post_data = UserFactory()
        self.company_user_post_data = CompanyFactory()
        self.taxpayer_post_data = TaxPayerArgentinaFactory(company=self.company_user_post_data)

        self.invoice_creation_empty_data = {}
        self.file_mock = MagicMock(spec=File)
        self.file_mock.name = 'test.pdf'
        self.file_mock.size = 50
        self.po_file_mock = MagicMock(spec=File)
        self.po_file_mock.name = 'test.pdf'
        self.po_file_mock.size = 50

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
        mail.outbox = []
        if self.file_mock and path.exists('file/{}'.format(self.file_mock.name)):
            remove('file/{}'.format(self.file_mock.name))
