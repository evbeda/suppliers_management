from parameterized import parameterized
from unittest.mock import patch

from django.core import mail
from django.test import (
    TestCase,
)

from invoices_app import (
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_PENDING,
    INVOICE_STATUS_CHANGES_REQUEST,
    INVOICE_STATUS_PAID,
    INVOICE_STATUS_REJECTED
)

from supplier_app import email_notifications

from supplier_app.tests.factory_boy import (
    CompanyUserPermissionFactory,
    TaxPayerFactory,
    CompanyFactory,
)


from users_app.factory_boy import (
    UserFactory
)
from utils.exceptions import CouldNotSendEmailError
from utils.invoice_lookup import invoice_status_lookup
from utils.send_email import (
    get_user_emails_by_tax_payer_id,
    send_email_notification,
    taxpayer_notification,
)


class EmailUtilsTest(TestCase):
    def setUp(self):
        self.company1 = CompanyFactory(
            name='Test',
            description='Test description',
        )
        self.company2 = CompanyFactory(
            name='Test2',
            description='Test description',
        )
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.user3 = UserFactory()
        self.user4 = UserFactory()
        self.user5 = UserFactory()
        self.permission1 = CompanyUserPermissionFactory(
            company=self.company1,
            user=self.user1
        )
        self.permission2 = CompanyUserPermissionFactory(
            company=self.company1,
            user=self.user2
        )
        self.permission3 = CompanyUserPermissionFactory(
            company=self.company1,
            user=self.user3
        )
        self.permission4 = CompanyUserPermissionFactory(
            company=self.company2,
            user=self.user4
        )
        self.permission5 = CompanyUserPermissionFactory(
            company=self.company2,
            user=self.user5
        )
        self.tax_payer1 = TaxPayerFactory(company=self.company1)
        self.tax_payer2 = TaxPayerFactory(company=self.company1)
        self.tax_payer3 = TaxPayerFactory(company=self.company2)

    def tearDown(self):
        mail.outbox = []

    def test_send_email_notification(self):
        subject = 'Testing title'
        message = 'Testing message'
        recipient_list = ['someone@somemail.com']

        send_email_notification(subject, message, recipient_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Testing title')

    def test_send_email_notification_raises_exception_with_wrong_recipient_list_format(self):
        subject = 'Testing title'
        message = 'Testing message'
        recipient_list = 'not_a_list_of_mail@test.com'
        with self.assertRaises(CouldNotSendEmailError):
            send_email_notification(subject, message, recipient_list)

    @patch(
        'utils.send_email.send_mail',
        side_effect=Exception
    )
    def test_send_email_notification_raises_exception(self, mocked_email_host):
        subject = 'Testing title'
        message = 'Testing message'
        recipient_list = ['someone@somemail.com']
        with self.assertRaises(CouldNotSendEmailError):
            send_email_notification(subject, message, recipient_list)

    def test_get_users_email_from_company(self):
        mails = [self.user4.email, self.user5.email]
        self.assertEqual(mails, get_user_emails_by_tax_payer_id(self.tax_payer3.id))

    def test_send_email_notification_to_emails_from_same_company(self):
        subject = 'Testing title'
        message = 'Testing message'
        recipient_list = get_user_emails_by_tax_payer_id(self.tax_payer3.id)
        send_email_notification(subject, message, recipient_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 2)
        self.assertEqual(mail.outbox[0].to, recipient_list)
        self.assertEqual(mail.outbox[0].subject, 'Testing title')

    @parameterized.expand([
        ('taxpayer_approval',),
        ('taxpayer_change_required',),
        ('taxpayer_denial',),
    ])
    def test_taxpayer_email_notification(self, change_type):
        taxpayer_notification(self.tax_payer1, change_type)
        self.assertEqual(
            email_notifications[change_type]['subject'],
            mail.outbox[0].subject,
        )

    def test_business_name_in_subject_for_taxpayer_email_notification(self):
        taxpayer_notification(self.tax_payer1, 'taxpayer_approval')
        self.assertIn(
            self.tax_payer1.business_name,
            mail.outbox[0].alternatives[0][0]
        )


class TestInvoiceStatusLookup(TestCase):

    @parameterized.expand([
        ('1', INVOICE_STATUS_APPROVED,),
        ('2', INVOICE_STATUS_PENDING,),
        ('3', INVOICE_STATUS_CHANGES_REQUEST,),
        ('4', INVOICE_STATUS_REJECTED),
        ('5', INVOICE_STATUS_PAID,),
    ])
    def test_invoice_status_lookup(self, expected_value, tag):
        self.assertEqual(invoice_status_lookup(tag), expected_value)
