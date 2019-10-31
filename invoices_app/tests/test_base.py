from os import (
    path,
    remove
)
from unittest.mock import MagicMock

from django.contrib.auth.models import Group
from django.core.files import File
from django.test import (
    Client,
    TestCase
)
from django.core import mail
from invoices_app.factory_boy import InvoiceFactory

from supplier_app import TAXPAYER_STATUS_APPROVED
from supplier_app.tests.factory_boy import (
    AddressFactory,
    CompanyFactory,
    CompanyUserPermissionFactory,
    EBEntityFactory,
    TaxPayerArgentinaFactory,
)

from users_app.factory_boy import UserFactory
from users_app.models import User


class TestBase(TestCase):

    def setUp(self):
        self.ap_user = User.objects.create_user(email='ap@eventbrite.com')
        ap_group = Group.objects.get(name='ap_admin')
        self.ap_user.groups.add(ap_group)

        self.user = UserFactory()
        supplier_group = Group.objects.get(name='supplier')
        self.user.groups.add(supplier_group)
        self.company = CompanyFactory()
        self.taxpayer = TaxPayerArgentinaFactory(company=self.company, taxpayer_state=TAXPAYER_STATUS_APPROVED)
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
        self.other_user.groups.add(supplier_group)
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

        self.eb_entity_example = EBEntityFactory()
        self.invoice_post_data = {
                'currency': 'ARS',
                'invoice_date': '2019-10-01',
                'invoice_file': self.file_mock,
                'invoice_number': '987654321',
                'invoice_type': 'A',
                'eb_entity': self.eb_entity_example.id,
                'net_amount': '4000',
                'po_number': '98876',
                'taxpayer': self.taxpayer.id,
                'total_amount': '5200',
                'vat': '1200',
                'user': self.user.id,
            }

        self.client = Client()

    def tearDown(self):
        mail.outbox = []
        if self.file_mock and path.exists('file/{}'.format(self.file_mock.name)):
            remove('file/{}'.format(self.file_mock.name))

    def get_invoice_post_data(
        self,
        eb_entity=None,
        invoice_file=None,
        taxpayer=None,
        user=None,
    ):
        return {
                'currency': 'ARS',
                'invoice_date': '2019-10-01',
                'invoice_file': invoice_file or self.file_mock,
                'invoice_number': '987654321',
                'invoice_type': 'A',
                'eb_entity': eb_entity or self.eb_entity_example.id,
                'net_amount': '4000',
                'po_number': '98876',
                'taxpayer': taxpayer or self.taxpayer.id,
                'total_amount': '5200',
                'vat': '1200',
                'user': user or self.user.id,
        }
