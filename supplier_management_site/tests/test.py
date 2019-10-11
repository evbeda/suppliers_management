from django.core import mail
from django.test import RequestFactory, TestCase
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from parameterized import parameterized

from invoices_app import (INVOICE_STATUS_APPROVED,
                          INVOICE_STATUS_CHANGES_REQUEST, INVOICE_STATUS_NEW,
                          INVOICE_STATUS_PAID, INVOICE_STATUS_REJECTED)
from supplier_app.tests.factory_boy import (CompanyFactory,
                                            CompanyUserPermissionFactory,
                                            TaxPayerFactory)
from supplier_management_site.tests.test_base import TestBase
from supplier_management_site.tests.views import home
from users_app.factory_boy import UserFactory
from utils.invoice_lookup import invoice_status_lookup
from utils.send_email import (get_user_emails_by_tax_payer_id,
                              send_email_notification)


class TestTranslationConfiguration(TestBase):
    def setUp(self):
        super(TestTranslationConfiguration, self).setUp()
        self.factory = RequestFactory()

    def tearDown(self):
        super(TestTranslationConfiguration, self).tearDown()
        activate('en')

    def test_plain_translation(self):
        activate('es')
        self.assertEqual(_('Hello world'), 'Hola Mundo')

    @parameterized.expand([
        ('en', 'Hello world'),
        ('es', 'Hola Mundo'),
        ('pt-BR', 'Olá, mundo!'),
    ])
    def test_testing_page_contains_correct_translation(self, lang, text):
        activate(lang)
        request = self.factory.get("/{}/".format(lang))
        response = home(request)
        self.assertContains(response, text)


class EmailUtilsTest(TestBase):
    def setUp(self):
        super(EmailUtilsTest, self).setUp()
        self.user2 = UserFactory()
        self.user3 = UserFactory()

        self.companyuserpermission2 = CompanyUserPermissionFactory(
            company=self.company,
            user=self.user2
        )
        self.companyuserpermission3 = CompanyUserPermissionFactory(
            company=self.company,
            user=self.user3
        )

    def tearDown(self):
        super(EmailUtilsTest, self).tearDown()
        mail.outbox = []

    def test_send_email_notification(self):
        subject = 'Testing title'
        message = 'Testing message'
        recipient_list = ['someone@somemail.com']

        send_email_notification(subject, message, recipient_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Testing title')

    def test_get_users_email_from_company(self):
        mails = [self.user.email, self.user2.email, self.user3.email]
        self.assertEqual(mails, get_user_emails_by_tax_payer_id(self.taxpayer.id))

    def test_send_email_notification_to_emails_from_same_company(self):
        subject = 'Testing title'
        message = 'Testing message'
        recipient_list = get_user_emails_by_tax_payer_id(self.taxpayer.id)
        send_email_notification(subject, message, recipient_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 3)
        self.assertEqual(mail.outbox[0].to, recipient_list)
        self.assertEqual(mail.outbox[0].subject, 'Testing title')


class TestInvoiceStatusLookup(TestBase):

    @parameterized.expand([
        ('1', INVOICE_STATUS_APPROVED,),
        ('2', INVOICE_STATUS_NEW,),
        ('3', INVOICE_STATUS_CHANGES_REQUEST,),
        ('4', INVOICE_STATUS_REJECTED),
        ('5', INVOICE_STATUS_PAID,),
    ])
    def test_invoice_status_lookup(self, expected_value, tag):
        self.assertEqual(invoice_status_lookup(tag), expected_value)
