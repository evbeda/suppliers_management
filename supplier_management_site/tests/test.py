from parameterized import parameterized

from django.core import mail
from django.test import TestCase, RequestFactory
from django.utils.translation import activate, ugettext_lazy as _

from supplier_management_site.tests.views import (
    home,
)

from utils.send_email import send_email_notification


class TestTranslationConfiguration(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
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


class EmailUtilsTest(TestCase):
    def tearDown(self):
        mail.outbox = []

    def test_send_email_notification(self):
        subject = 'Testing title'
        message = 'Testing message'
        recipient_list = ['someone@somemail.com']

        send_email_notification(subject, message, recipient_list)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Testing title')
