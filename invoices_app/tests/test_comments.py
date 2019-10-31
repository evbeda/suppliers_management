from http import HTTPStatus
from parameterized import parameterized
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from invoices_app import (
    INVOICE_STATUS_CHANGES_REQUEST,
    INVOICE_MAX_SIZE_FILE
)
from invoices_app.factory_boy import InvoiceFactory
from invoices_app.models import Comment
from invoices_app.tests.test_base import TestBase

from supplier_app.tests.factory_boy import CompanyUserPermissionFactory

from users_app.factory_boy import UserFactory

from utils.invoice_lookup import invoice_status_lookup
from utils.history import invoice_history_comments


class CommentsTest(TestBase):
    # Feature: Generates comments when invoice state changes
    @parameterized.expand([
        ('CHANGES REQUESTED',),
        ('REJECTED'),
        ('PAID',),
    ])
    @patch('invoices_app.views._send_email_when_change_invoice_status')
    def test_generate_a_comment_when_invoice_changes_his_state(
        self,
        new_status,
        _
    ):
        # Given an invoice and a logged AP
        # invoice : self.invoice
        self.client.force_login(self.ap_user)
        old_status = self.invoice.get_status_display()
        # When AP changes its state
        response = self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': self.invoice.id,
                }
            ),
            {'status': invoice_status_lookup(new_status)}
        )

        # Then the invoice should have a comment associated to it with its message
        comment = invoice_history_comments(self.invoice)[0]
        self.assertEqual(
            comment.message,
            'Changed: \n{} from {} to {}\n'.format(
                'Status',
                old_status,
                new_status
            )
        )
        self.assertEqual(comment.user, self.ap_user)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)

    @patch('invoices_app.views._send_email_when_editing_invoice')
    def test_supplier_invoice_edit_and_it_exists_a_new_comment(self, _):
        # Given an invoice and a logged Supplier
        # invoice : self.invoice
        self.client.force_login(self.user)
        old_invoice_number = self.invoice.invoice_number
        self.invoice.status = invoice_status_lookup(INVOICE_STATUS_CHANGES_REQUEST)
        self.invoice.save()

        # When a supplier edits the invoice
        response = self.client.post(
            reverse(
                'taxpayer-invoice-update',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice.id
                }
            ),
            self.invoice_post_data
        )
        # Then the invoice should have a comment associated to it with its message
        comment = invoice_history_comments(self.invoice)[-1]
        self.assertIn(
            '{} from 1234 to 987654321'.format(
                'Invoice Number',
                old_invoice_number,
                self.invoice.invoice_number,
            ),
            comment.message,
        )
        self.assertEqual(comment.user, self.user)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)

    @parameterized.expand([
        ('Valid text', HTTPStatus.FOUND),
    ])
    @patch('invoices_app.views._send_email_when_posting_a_comment')
    def test_ap_can_add_a_comment_in_an_invoice(
        self,
        message,
        expected_status_code,
        _,
    ):
        # Given an invoice and a logged AP
        # invoice : self.invoice
        self.client.force_login(self.ap_user)

        # When AP writes a comment
        response = self.client.post(
            reverse(
                'post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {'message': message}
        )

        # Then the invoice should have a comment associated to it with its message
        comment = Comment.objects.filter(
            invoice=self.invoice
        ).latest('comment_date_received')

        self.assertEqual(expected_status_code, response.status_code)
        self.assertEqual(
            comment.message,
            message
        )
        self.assertEqual(comment.user, self.ap_user)

    @parameterized.expand([
        ('Valid text', HTTPStatus.FOUND),
    ])
    def test_supplier_can_add_a_comment_in_an_invoice(
        self,
        message,
        expected_status_code
    ):
        # Given an invoice and a logged supplier
        # invoice : self.invoice
        self.client.force_login(self.user)

        # When AP writes a comment
        response = self.client.post(
            reverse(
                'post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {'message': message}
        )

        # Then the invoice should have a comment associated to it with its message
        comment = Comment.objects.filter(
            invoice=self.invoice
        ).latest('comment_date_received')

        self.assertEqual(expected_status_code, response.status_code)
        self.assertEqual(
            comment.message,
            message
        )
        self.assertEqual(comment.user, self.user)

    def test_post_an_empty_comment(self):
        # Given an invoice and a logged AP
        # invoice : self.invoice
        self.client.force_login(self.ap_user)

        # When AP writes an empty comment
        response = self.client.post(
            reverse(
                'post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {'message': ''}
        )

        # Then an error should appear
        self.assertEqual(HTTPStatus.BAD_REQUEST, response.status_code)

    @parameterized.expand([
        ('Valid text', HTTPStatus.FOUND),
    ])
    def test_comment_to_an_invoice_within_the_company_and_same_tax_payer(
        self,
        message,
        expected_status_code
    ):
        # Given an invoice and user (supplier)
        # from other taxpayer but the same company
        self.client.force_login(self.user)

        self.user_for_same_taxpayer = UserFactory()
        self.companyuserpermission = CompanyUserPermissionFactory(
            company=self.company,
            user=self.user_for_same_taxpayer
        )
        self.invoice = InvoiceFactory(
            user=self.user,
            taxpayer=self.taxpayer,
            invoice_number='8695030'
        )

        # When the user posts a comment
        response = self.client.post(
            reverse(
                'post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {'message': message}
        )

        # Then the invoice should have a comment associated to it with its message
        comment = Comment.objects.filter(
            invoice=self.invoice
        ).latest('comment_date_received')

        self.assertEqual(expected_status_code, response.status_code)
        self.assertEqual(
            comment.message,
            message
        )
        self.assertEqual(comment.user, self.user)

    def test_comment_to_an_invoice_not_of_the_company(self):
        # Given an invoice and user (supplier)
        # from other taxpayer but from other company
        self.client.force_login(self.user)

        # When the user posts a comment
        response = self.client.post(
            reverse(
                'post-comment',
                kwargs={
                    'pk': self.invoice_from_other_user.id,
                },
            ),
            {'message': 'Valid Text'}
        )
        # Then an error should appear
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

    def test_post_a_comment_without_a_logged_user(self):
        # Given an invoice and a not logged user
        # invoice: self.invoice
        # user: self.user

        # When the user posts a comment
        response = self.client.post(
            reverse(
                'post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {'message': 'Valid Text'}
        )

        # Then an error should appear
        self.assertEqual(HTTPStatus.FORBIDDEN, response.status_code)

    def test_comment_redirects_to_invoice_detail_view(self):
        # Given an invoice and a logged user
        # invoice: self.invoice
        self.client.force_login(self.user)

        # When the user posts a comment
        response = self.client.post(
            reverse(
                'post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {'message': 'Valid Text'}
        )

        # Then it redirects to InvoiceDetailView
        self.assertRedirects(
            response,
            '/invoices/taxpayer/{}/detail/{}/'.format(
                self.invoice.taxpayer.id,
                self.invoice.id,
            )
        )

    @parameterized.expand([
        ('Valid text', HTTPStatus.FOUND),
    ])
    @patch('invoices_app.views._send_email_when_posting_a_comment')
    def test_ap_can_add_a_comment_in_an_invoice_with_a_file(
        self,
        message,
        expected_status_code,
        _
    ):
        # Given an invoice and a logged AP
        # invoice : self.invoice
        self.client.force_login(self.ap_user)

        # When AP writes a comment
        response = self.client.post(
            reverse(
                'post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {
                'message': message,
                'invoice_file': self.file_mock,
            }
        )

        # Then the invoice should have a comment associated to it with its message
        comment = Comment.objects.filter(
            invoice=self.invoice
        ).latest('comment_date_received')

        self.assertEqual(expected_status_code, response.status_code)
        self.assertEqual(
            comment.message,
            message
        )
        self.assertEqual(comment.user, self.ap_user)
        self.assertTrue(self.file_mock.name in comment.comment_file.name)

    @parameterized.expand([
        ('Valid text', HTTPStatus.FOUND),
    ])
    def test_supplier_can_add_a_comment_in_an_invoice_with_a_file(
        self,
        message,
        expected_status_code,
    ):
        # Given an invoice, a logged supplier and a file
        # invoice : self.invoice
        # file: self.file_mock
        self.client.force_login(self.user)

        # When supplier writes a comment
        response = self.client.post(
            reverse(
                'post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {
                'message': message,
                'invoice_file': self.file_mock
            }
        )

        # Then the invoice should have a comment associated to it with its message
        comment = Comment.objects.filter(
            invoice=self.invoice
        ).latest('comment_date_received')

        self.assertEqual(expected_status_code, response.status_code)
        self.assertEqual(
            comment.message,
            message
        )
        self.assertEqual(comment.user, self.user)
        self.assertTrue(self.file_mock.name in comment.comment_file.name)

    @parameterized.expand([
        ('test.xml', 20, ['Only .pdf allowed']),
        ('test.pdf', 5242881, [
            'The file size is greater than {}MB.'.format(int(INVOICE_MAX_SIZE_FILE/(1024*1024)))]),
        ('test.xml', 5242881, [
            'Only .pdf allowed', 'The file size is greater than {}MB.'.format(int(INVOICE_MAX_SIZE_FILE/(1024*1024)))])
    ])
    def test_supplier_adds_an_invalid_file_in_a_comment(
        self,
        name_file,
        size_file,
        messages
    ):
        # Given an invoice, a logged supplier and a file
        # invoice : self.invoice
        self.client.force_login(self.user)
        # When supplier writes a comment
        response = self.client.post(
            reverse(
                'post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {
                'message': 'Valid Text',
                'invoice_file': SimpleUploadedFile(name_file, bytes(size_file)),
            },
            follow=True
        )
        # Then a message should appear
        for message in messages:
            self.assertContains(response, message)

    @parameterized.expand([
        ('test.xml', 20,),
        ('test.pdf', 5242881,),
        ('test.xml', 5242881,)
    ])
    def test_supplier_adds_an_invalid_file_in_a_comment_and_no_comment_is_created(
        self,
        name_file,
        size_file,
    ):
        # Given an invoice, a logged supplier and a file
        # invoice : self.invoice
        self.client.force_login(self.user)
        # When supplier writes a comment
        self.client.post(
            reverse(
                'post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {
                'message': 'Valid Text',
                'invoice_file': SimpleUploadedFile(name_file, bytes(size_file)),
            },
            follow=True
        )
        # Then no comment should be created
        self.assertFalse(Comment.objects.all())
