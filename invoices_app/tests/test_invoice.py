from datetime import date, timedelta
from functools import reduce
from http import HTTPStatus
from parameterized import parameterized
from unittest.mock import patch


from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import Form
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import get_language
from django.shortcuts import get_object_or_404
from django.core import mail

from supplier_app.constants.taxpayer_status import TAXPAYER_STATUS_PENDING
from supplier_app.tests.factory_boy import CompanyUserPermissionFactory
from supplier_app.tests.factory_boy import TaxPayerEBEntityFactory
from users_app.factory_boy import UserFactory

from invoices_app import (
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_PENDING,
    INVOICE_STATUS_REJECTED,
    INVOICE_STATUS_CHANGES_REQUEST,
    INVOICE_STATUS_PAID,
    INVOICE_MAX_SIZE_FILE,
    NO_WORKDAY_ID_ERROR,
    INVOICE_STATUS_IN_PROGRESS)
from invoices_app.factory_boy import InvoiceFactory
from invoices_app.forms import InvoiceForm
from invoices_app.models import Invoice
from invoices_app.tests.test_base import TestBase
from invoices_app.views import (
    _send_email_when_change_invoice_status,
    _send_email_when_posting_a_comment,
    _send_email_when_editing_invoice
)

from utils.invoice_lookup import invoice_status_lookup


class TestInvoice(TestBase):

    def test_invoice_create(self):
        form = InvoiceForm(
            data=self.invoice_post_data,
            files={
                'invoice_file': self.file_mock,
            }
        )
        self.assertTrue(form.is_valid())

    def test_invoice_create_required_fields(self):
        self.invoice_post_data['invoice_number'] = ''
        form = InvoiceForm(
            data=self.invoice_post_data
        )
        self.assertFalse(form.is_valid())

    @parameterized.expand([
        ('test.pdf', 20, True),
        ('test.xml', 20, False),
        ('test.pdf', 500000000, False),
        ('test.xml', 500000000, False),
    ])
    def test_form_file_is_valid(self, name_file, size_file, expected):
        form = InvoiceForm(
            data=self.invoice_post_data,
            files={
                'invoice_file': SimpleUploadedFile(name_file, bytes(size_file)),
            }
        )
        self.assertEqual(form.is_valid(), expected)

    @parameterized.expand([
        ('test.xml', 20, ["File extension 'xml' is not allowed. Allowed extensions are: 'pdf'."]),
        ('test.pdf', 5242881, [
            'File size 5MB is not allowed.\n Limit size: {}MB.'.format(int(INVOICE_MAX_SIZE_FILE/(1024*1024)))
            ]),
        ('test.xml', 5242881, [
            "File extension 'xml' is not allowed. Allowed extensions are: 'pdf'.",
            'File size 5MB is not allowed.\n Limit size: {}MB.'.format(int(INVOICE_MAX_SIZE_FILE/(1024*1024)))
        ])
    ])
    def test_invoice_file_is_valid_message(
        self,
        name_file,
        size_file,
        messages
    ):
        form = InvoiceForm(
            data=self.invoice_post_data,
            files={
                'invoice_file': SimpleUploadedFile(name_file, bytes(size_file)),
            }
        )
        form.is_valid()
        errors = reduce(lambda a, b: a+b, form.errors.values())
        for message in messages:
            self.assertTrue(message in errors)

    def test_invoice_create_db(self):
        self.assertEqual(
            Invoice.objects.get(invoice_number='1234'),
            self.invoice
        )

    def test_invoice_create_view(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('invoice-create', kwargs={'taxpayer_id': self.taxpayer.id}),
            self.invoice_post_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        invoice = Invoice.objects.get(invoice_number=self.invoice_post_data['invoice_number'])
        self.assertEqual(invoice.status, invoice_status_lookup(INVOICE_STATUS_PENDING))

    def test_invoice_should_only_display_eb_entities_from_the_taxpayer(self):
        self.client.force_login(self.user)
        taxpayer_eb_entity_1 = TaxPayerEBEntityFactory(taxpayer=self.taxpayer)
        taxpayer_eb_entity_2 = TaxPayerEBEntityFactory(taxpayer=self.taxpayer)
        response = self.client.get(
            reverse('invoice-create', kwargs={'taxpayer_id': self.taxpayer.id})
        )
        taxpayer_eb_entities = \
            [e.eb_entity for e in self.taxpayer.taxpayerebentity_set.all()]
        self.assertEqual(
            response.context_data['eb_entities'],
            taxpayer_eb_entities
        )
        self.assertContains(response, taxpayer_eb_entity_1.eb_entity.eb_name)
        self.assertContains(response, taxpayer_eb_entity_2.eb_entity.eb_name)

    def test_invoice_create_should_be_related_with_eb_entity(self):
        self.client.force_login(self.user)
        taxpayer_eb_entity_1 = TaxPayerEBEntityFactory(taxpayer=self.taxpayer)
        self.client.post(
            reverse('invoice-create', kwargs={'taxpayer_id': self.taxpayer.id}),
            self.get_invoice_post_data(eb_entity=taxpayer_eb_entity_1.eb_entity.id),
        )
        self.assertEqual(
            taxpayer_eb_entity_1.eb_entity,
            Invoice.objects.last().invoice_eb_entity
        )

    def test_invoice_create_existing_invoice_id(self):
        self.client.force_login(self.user)
        self.invoice_post_data['invoice_number'] = self.invoice.invoice_number
        response = self.client.post(
            reverse('invoice-create', kwargs={'taxpayer_id': self.taxpayer.id}),
            self.invoice_post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response,
            'The invoice {} already exists'.format(self.invoice.invoice_number)
        )

    def test_supplier_invoices_list_view(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('supplier-invoice-list', kwargs={'taxpayer_id': self.taxpayer.id}),
        )
        self.assertContains(response, self.invoice.po_number)
        self.assertContains(response, self.invoice.status)

    def test_supplier_invoices_list_only_taxpayer_invoices(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('supplier-invoice-list', kwargs={'taxpayer_id': self.taxpayer.id}),
        )
        # Only the invoice with from the tax payer should be listed.
        self.assertIn(
            self.invoice.taxpayer.id,
            [self.taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertNotIn(
            self.invoice_from_other_user.taxpayer.id,
            [self.taxpayer.id for taxpayer in response.context['object_list']]
        )

    def test_supplier_with_two_invoices_list_only_two_invoices(self):
        self.client.force_login(self.other_user)
        invoice2 = InvoiceFactory(
            user=self.other_user,
            taxpayer=self.taxpayer_for_other_user,
            invoice_number=1237
        )

        response = self.client.get(
            reverse('invoices-list')
        )
        # Only the invoice with from the tax payer should be listed.
        self.assertIn(
            self.invoice_from_other_user.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertIn(
            invoice2.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertEqual(2, len(response.context_data['object_list']))

    def test_AP_should_see_all_invoices(self):
        self.client.force_login(self.ap_user)

        invoice2_user1 = InvoiceFactory(
            user=self.user,
            taxpayer=self.taxpayer,
            invoice_number=1238
        )
        invoice2_other_user = InvoiceFactory(
            user=self.other_user,
            taxpayer=self.taxpayer_for_other_user,
            invoice_number=1239
        )
        response = self.client.get(
            reverse('invoices-list')
        )
        self.assertIn(
            self.invoice.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertIn(
            self.invoice_from_other_user.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertIn(
            invoice2_user1.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertIn(
            invoice2_other_user.taxpayer.id,
            [taxpayer.id for taxpayer in response.context['object_list']]
        )
        self.assertEqual(4, len(response.context_data['object_list']))

    def test_supplier_invoices_list_404_if_invalid_supplier(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('supplier-invoice-list', kwargs={'taxpayer_id': 999}),
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    @parameterized.expand([
        (INVOICE_STATUS_REJECTED),
        (INVOICE_STATUS_PAID,),
    ])
    @patch('invoices_app.views._send_email_when_change_invoice_status')
    def test_invoice_change_status_in_db(
        self,
        status,
        _
    ):
        self.client.force_login(self.ap_user)
        self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': self.invoice.id,
                }
            ),
            {'status': invoice_status_lookup(status), }
        )

        invoice = get_object_or_404(Invoice, pk=self.invoice.id)
        self.assertEqual(invoice.status, invoice_status_lookup(status))

    def test_invoice_change_status_not_in_available_status(self):
        self.client.force_login(self.ap_user)
        request = self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': self.invoice.id,
                }
            ),
            {'status': 'NOT_STATUS', }
        )
        self.assertEqual(request.status_code, 400)

    def test_invoice_change_status_only_ap_fail(self):
        self.client.force_login(self.user)
        request = self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': self.invoice.id,
                }
            ),
            {'status': invoice_status_lookup(INVOICE_STATUS_APPROVED), }
        )
        self.assertEqual(request.status_code, HTTPStatus.FORBIDDEN)

    @parameterized.expand([
        (1, 302),
        (31, 404),
    ])
    @patch('invoices_app.views._send_email_when_change_invoice_status')
    def test_invoice_change_status_code(
        self,
        id,
        expected,
        _
    ):
        self.client.force_login(self.ap_user)
        request = self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': id,
                }
            ),
            {
                'status': invoice_status_lookup(INVOICE_STATUS_REJECTED),
            }
        )
        self.assertEqual(request.status_code, expected)

    def test_invoice_change_status_to_approved_no_workday_id(self):
        self.client.force_login(self.ap_user)
        request = self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': self.invoice.id,
                }
            ),
            {
                'status': invoice_status_lookup(INVOICE_STATUS_IN_PROGRESS),
            },
            follow=True
        )
        self.assertContains(request, NO_WORKDAY_ID_ERROR)

    def test_invoice_in_progress_in_db(self):
        self.client.force_login(self.ap_user)
        self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': self.invoice.id,
                }
            ),
            {
                'status': invoice_status_lookup(INVOICE_STATUS_IN_PROGRESS),
                'workday_id': 123123,
            },
            follow=True
        )

        invoice = get_object_or_404(Invoice, pk=self.invoice.id)
        self.assertEqual(invoice.status, invoice_status_lookup(INVOICE_STATUS_IN_PROGRESS))
        self.assertEqual(invoice.workday_id, 123123)

    def test_invoice_change_status_code_to_approved(self):
        self.client.force_login(self.ap_user)
        request = self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': self.invoice.id,
                }
            ),
            {
                'status': invoice_status_lookup(INVOICE_STATUS_APPROVED),
                'workday_id': 123123,
            }
        )
        self.assertEqual(request.status_code, 302)

    def test_invoice_change_status_invalid_workday_id(self):
        self.client.force_login(self.ap_user)
        response = self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': self.invoice.id,
                }
            ),
            {
                'status': invoice_status_lookup(INVOICE_STATUS_IN_PROGRESS),
                'workday_id': "invalid id",
            },
            follow=True
        )
        self.assertContains(response, 'Enter a valid integer.')

    def test_supplier_invoice_edit(self):
        self.client.force_login(self.user)
        self.invoice.status = invoice_status_lookup(INVOICE_STATUS_CHANGES_REQUEST)
        self.invoice.save()
        res = self.client.post(
            reverse(
                'taxpayer-invoice-update',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice.id
                }
            ),
            self.invoice_post_data,
        )
        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.invoice.refresh_from_db()
        self.assertEqual(
            self.invoice.invoice_number,
            self.invoice_post_data['invoice_number']
        )
        self.assertEqual(
            self.invoice.status,
            invoice_status_lookup(INVOICE_STATUS_PENDING)
        )

    @patch('invoices_app.views._send_email_when_editing_invoice')
    def test_ap_invoice_edit(self, _):
        self.client.force_login(self.ap_user)
        res = self.client.post(
            reverse(
                'invoice-update',
                kwargs={
                    'pk': self.invoice.id
                }
            ),
            self.invoice_post_data,
        )
        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.invoice.refresh_from_db()
        self.assertEqual(
            self.invoice.invoice_number,
            self.invoice_post_data['invoice_number']
        )
        self.assertEqual(
            self.invoice.status,
            invoice_status_lookup(INVOICE_STATUS_PENDING)
        )

    def test_supplier_invalid_invoice_edit_request(self):
        self.client.force_login(self.user)
        self.invoice.status = invoice_status_lookup(INVOICE_STATUS_CHANGES_REQUEST)
        self.invoice.save()

        old_invoice_number = self.invoice.invoice_number
        res = self.client.post(
            reverse(
                'taxpayer-invoice-update',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice.id
                }
            ),
            {}
        )
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.invoice.refresh_from_db()
        self.assertEqual(
            self.invoice.invoice_number,
            old_invoice_number
        )
        self.assertContains(res, 'This field is required.')

    @patch('invoices_app.views._send_email_when_editing_invoice')
    def test_supplier_invoice_edit_permissions(self, _):
        self.client.force_login(self.user)

        self.invoice.status = invoice_status_lookup(INVOICE_STATUS_CHANGES_REQUEST)
        self.invoice.save()
        res = self.client.post(
            reverse(
                'taxpayer-invoice-update',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice.id
                }
            ),
            self.invoice_post_data,
            follow=True,
        )
        self.assertIn(
            (reverse('supplier-invoice-list', kwargs={'taxpayer_id': self.taxpayer.id}), 302),
            res.redirect_chain
        )
        self.assertEqual(res.status_code, HTTPStatus.OK)

    @patch('invoices_app.views._send_email_when_editing_invoice')
    def test_ap_invoice_edit_permissions(self, _):
        self.client.force_login(self.ap_user)
        self.invoice.status = invoice_status_lookup(INVOICE_STATUS_APPROVED)
        self.invoice.save()
        res = self.client.post(
            reverse(
                'taxpayer-invoice-update',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice.id
                }
            ),
            self.invoice_post_data,
        )
        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.invoice.refresh_from_db()
        self.assertEqual(
            self.invoice.invoice_number,
            self.invoice_post_data['invoice_number']
        )

    def test_supplier_invoice_detail_view_address(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'invoices-detail',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice.id
                }
            )
        )

        self.assertEqual(
            response.context['address'],
            self.address
        )

    def test_ap_invoice_detail_view_address(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse(
                'invoices-detail',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice.id
                }
            )
        )
        self.assertEqual(response.context['address'], self.address)

    def test_invoices_list_filter_status(self):
        self.client.force_login(self.ap_user)
        invoice_approved = InvoiceFactory(
            user=self.user,
            taxpayer=self.taxpayer,
            invoice_number='4321'
        )
        invoice_approved.status = invoice_status_lookup(INVOICE_STATUS_APPROVED)
        invoice_approved.save()

        response = self.client.get(
            '{}?{}'.format(
                reverse('invoices-list'),
                'status={}'.format(invoice_status_lookup(INVOICE_STATUS_APPROVED)))
        )
        self.assertContains(
            response,
            invoice_approved.invoice_number
        )
        self.assertNotContains(
            response,
            self.invoice.invoice_number
        )

    def test_invoices_list_filter_invoice_date(self):
        self.client.force_login(self.ap_user)
        invoice_old = InvoiceFactory(
            user=self.user,
            taxpayer=self.taxpayer,
            invoice_number='4321',
            invoice_date=date(2019, 1, 1)
        )
        response = self.client.get(
            '{}?{}'.format(reverse('invoices-list'), 'invoice_date_after=02/02/2019')
        )
        self.assertNotContains(
            response,
            invoice_old.invoice_number
        )
        self.assertContains(
            response,
            self.invoice.invoice_number
        )

    def test_invoices_list_filter_invoice_total_amount(self):
        self.client.force_login(self.ap_user)
        invoice_low_total_amount = InvoiceFactory(
            user=self.user,
            taxpayer=self.taxpayer,
            invoice_number='4321',
            total_amount=1,
        )
        invoice_high_total_amount = InvoiceFactory(
            user=self.user,
            taxpayer=self.taxpayer,
            invoice_number='98764',
            total_amount=100,
        )
        self.invoice.total_amount = 10
        self.invoice.save()

        response = self.client.get(
            '{}?{}&{}'.format(
                reverse('invoices-list'),
                'total_amount_min={}'.format(invoice_low_total_amount.total_amount+1),
                'total_amount_max={}'.format(invoice_high_total_amount.total_amount-1),
            ),
        )
        self.assertNotContains(
            response,
            invoice_low_total_amount.invoice_number
        )
        self.assertNotContains(
            response,
            invoice_high_total_amount.invoice_number
        )
        self.assertContains(
            response,
            self.invoice.invoice_number
        )

    def test_invoices_list_filter_taxpayer(self):
        self.client.force_login(self.ap_user)

        response = self.client.get(
            '{}?{}'.format(reverse('invoices-list'), 'taxpayer__business_name={}'.format(self.taxpayer.business_name))
        )
        self.assertContains(
            response,
            self.invoice.invoice_number
        )
        self.assertNotContains(
            response,
            self.invoice_from_other_user.invoice_number
        )

    def test_invoices_list_filter_taxpayer_country(self):
        self.client.force_login(self.ap_user)

        self.taxpayer_for_other_user.country = 'BR'
        self.taxpayer_for_other_user.save()

        response = self.client.get(
            '{}?{}'.format(reverse('invoices-list'), 'taxpayer__country={}'.format(self.taxpayer.country))
        )
        self.assertContains(
            response,
            self.invoice.invoice_number
        )
        self.assertNotContains(
            response,
            self.invoice_from_other_user.invoice_number
        )

    def test_invoice_create_calculate_due_date(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse('invoice-create', kwargs={'taxpayer_id': self.taxpayer.id}),
            self.invoice_post_data,
        )
        time_to_due = self.taxpayer.get_taxpayer_child().payment_term
        invoice = Invoice.objects.get(invoice_number=self.invoice_post_data['invoice_number'])
        self.assertEqual(invoice.invoice_due_date, invoice.invoice_date + timedelta(days=time_to_due))

    def test_send_email_when_ap_edits_invoice(self):
        self.client.force_login(self.ap_user)
        user2 = UserFactory()
        CompanyUserPermissionFactory(
            company=self.company,
            user=user2
        )
        user3 = UserFactory()
        CompanyUserPermissionFactory(
            company=self.company,
            user=user3
        )
        self.client.post(
            reverse(
                'taxpayer-invoice-update',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice.id
                }
            ),
            self.invoice_post_data
        )
        self.assertEqual(len(mail.outbox), 3)
        self.assertEqual(len(mail.outbox[0].to), 1)

    def test_do_not_send_email_when_user_edits_invoice(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse(
                'taxpayer-invoice-update',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice.id
                }
            ),
            self.invoice_post_data
        )
        self.assertEqual(len(mail.outbox), 0)

    @parameterized.expand([
        ('en', 'PAID', 'Invoice {} changed status to {}'),
        ('es', 'PAGADA', 'La factura {} cambió de estado a {}'),
        ('pt-br','PAGO', 'A fatura {} alterou o status para {}'),
    ])
    def test_send_email_when_change_invoice_status_with_user_preferred_language(
        self,
        language,
        new_status,
        expected_subject,
    ):
        # Given an invoice with a state, an user with a preferred language
        self.invoice.status = new_status
        self.invoice.save()

        self.user.preferred_language = language
        self.user.save()

        request = HttpRequest()
        request.user = self.user

        # When an email is sent when changing invoice status
        with patch('invoices_app.views._send_email') as patch_send_email:
            _send_email_when_change_invoice_status(request, self.invoice)

        # Then an email must be sent to user in his languages preferences
        params, _ = patch_send_email.call_args
        subject = params[0]

        self.assertEqual(
            subject,
            expected_subject.format(
                self.invoice.invoice_number,
                self.invoice.status
            )
        )

    @parameterized.expand([
        ('en', ),
        ('es', ),
        ('pt-br',),
    ])
    def test_session_language_remains_when_sending_email_in_change_invoice_status(
        self,
        language,
    ):
        # Given an user associated with the invoice with a preferred language
        # And another logged user within the company
        self.user.preferred_language = language
        self.user.save()

        self.logged_user = UserFactory()
        supplier_group = Group.objects.get(name='supplier')
        self.logged_user.groups.add(supplier_group)
        self.companyuserpermission = CompanyUserPermissionFactory(
            company=self.company,
            user=self.logged_user
        )

        request = HttpRequest()
        request.user = self.logged_user

        # When an email is sent when changing invoice status
        with patch('invoices_app.views._send_email'):
            _send_email_when_change_invoice_status(request, self.invoice)

        # Then session language of the logged user remain
        self.assertEqual(request.user.preferred_language, get_language())

    @parameterized.expand([
        ('en', 'Eventbrite Invoice {} commented',\
            'You have a new comment on Invoice # {}. Please check your invoice. COMMENT:{}'),
        ('es', 'Factura de Eventbrite {} comentada', \
            'Tienes un nuevo comentario en la factura # {}. Por favor revise su factura. COMENTARIO:{}'),
        ('pt-br', 'Fatura da Eventbrite {} comentada', \
            'Você tem um novo comentário na fatura # {}. Por favor, verifique sua fatura. COMENTE:{}'),
    ])
    def test_send_email_when_posting_a_comment_with_user_preferred_language(
        self,
        language,
        expected_subject,
        expected_message,
    ):
        # Given an invoice, an user with a preferred language
        # invoice: self.invoice
        self.user.preferred_language = language
        self.user.save()

        message = 'Valid message'

        request = HttpRequest()
        request.POST['message'] = message
        request.user = self.user

        # When an email is sent when posting a comment
        with patch('invoices_app.views._send_email') as patch_send_email:
            _send_email_when_posting_a_comment(request, self.invoice)

        # Then an email must be sent to user in his languages preferences
        params, _ = patch_send_email.call_args
        subject = params[0]

        self.assertEqual(
            subject,
            expected_subject.format(
                self.invoice.invoice_number,
            )
        )
        self.assertTrue(
            message.format(self.invoice.invoice_number, message) in params[1]
        )

    @parameterized.expand([
        ('en', ),
        ('es', ),
        ('pt-br',),
    ])
    def test_session_language_remains_when_sending_email_in_posting_a_comment(
        self,
        language,
    ):
        # Given an user associated with the invoice with a preferred language
        # And another logged user within the company
        self.user.preferred_language = language
        self.user.save()

        self.logged_user = UserFactory()
        supplier_group = Group.objects.get(name='supplier')
        self.logged_user.groups.add(supplier_group)
        self.companyuserpermission = CompanyUserPermissionFactory(
            company=self.company,
            user=self.logged_user
        )

        request = HttpRequest()
        request.POST['message'] = 'Valid message'
        request.user = self.logged_user

        # When an email is sent when posting a comment
        with patch('invoices_app.views._send_email'):
            _send_email_when_posting_a_comment(request, self.invoice)

        # Then session language of the logged user remain
        self.assertEqual(request.user.preferred_language, get_language())

    @parameterized.expand([
        ('en', 'Eventbrite Invoice Edited', "Your Invoice # {} was edited by an administrator. Please check your invoice"),
        ('es', 'Factura de Eventbrite editada', "Tu factura # {} fue modificada por un administrador. Por favor revise su factura."),
        ('pt-br', 'Fatura da Eventbrite editada', "Sua fatura # {} foi editada por um administrador. Verifique sua fatura"),
    ])
    def test_send_email_when_editing_an_invoice_in_user_preferred_language(
        self,
        language,
        expected_subject,
        expected_message,
    ):
        # Given an invoice with state CHANGES REQUIRED
        # An AP user and a supplier user with a preferred language

        # ap_user: self.ap_user
        self.invoice.status = invoice_status_lookup(INVOICE_STATUS_CHANGES_REQUEST)
        self.user.preferred_language = language
        self.user.save()

        form = Form()
        form.instance = self.invoice

        # When an email is sent when editing an invoice
        with patch('invoices_app.views._send_email') as patch_send_email:
            _send_email_when_editing_invoice(form.instance, self.ap_user)

        # Then an email must be sent to user in his languages preferences
        params, _ = patch_send_email.call_args
        subject = params[0]
        message = params[1]

        self.assertEqual(subject, expected_subject)
        self.assertTrue(
            expected_message.format(self.invoice.invoice_number, message) in params[1]
        )

    def test_invoice_export_to_xls(self):
        self.client.force_login(self.ap_user)
        response = self.client.get(
            reverse('invoice-to-xls'),
        )
        self.assertTrue(response._headers['content-disposition'][1].endswith('.xlsx'))

    def test_invoice_creation_when_taxpayer_is_not_approved(self):
        self.client.force_login(self.user)
        self.taxpayer.taxpayer_state = TAXPAYER_STATUS_PENDING
        self.taxpayer.save()

        response = self.client.post(
            reverse('invoice-create', kwargs={'taxpayer_id': self.taxpayer.id}),
            self.invoice_post_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Taxpayer not approved yet')

    def test_new_invoice_button_shows_when_approved(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('supplier-invoice-list', kwargs={'taxpayer_id': self.taxpayer.id}),
            self.invoice_post_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'New Invoice')

    def test_new_invoice_button_doesnt_show_when_not_approved(self):
        self.client.force_login(self.user)
        self.taxpayer.taxpayer_state = TAXPAYER_STATUS_PENDING
        self.taxpayer.save()

        response = self.client.get(
            reverse('supplier-invoice-list', kwargs={'taxpayer_id': self.taxpayer.id}),
            self.invoice_post_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotContains(response, 'New Invoice')
