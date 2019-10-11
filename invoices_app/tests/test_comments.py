from http import HTTPStatus
from parameterized import parameterized

from django.urls import reverse

from invoices_app import (
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_REJECTED,
    INVOICE_STATUS_CHANGES_REQUEST,
    INVOICE_STATUS_PAID,
)
from invoices_app.factory_boy import InvoiceFactory
from invoices_app.models import Comment
from supplier_management_site.tests.test_base import TestBase

from supplier_app.tests.factory_boy import CompanyUserPermissionFactory

from users_app.factory_boy import UserFactory

from utils.invoice_lookup import invoice_status_lookup


class CommentTest(TestBase):

    # Feature: Generates comments when invoice state changes
    @parameterized.expand([
        (INVOICE_STATUS_APPROVED,),
        (INVOICE_STATUS_CHANGES_REQUEST,),
        (INVOICE_STATUS_REJECTED),
        (INVOICE_STATUS_PAID,),
    ])
    def test_generate_a_comment_when_invoice_changes_his_state(
        self,
        new_status,
    ):
        # Given an invoice and a logged AP
        # invoice : self.invoice
        self.client.force_login(self.ap_user)

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
        comment = Comment.objects.filter(
            invoice=self.invoice
        ).latest('comment_date_received')

        self.assertEqual(
            str(comment),
            '{} has changed the invoice status to {}'.format(
                self.ap_user.email,
                new_status
            )
        )
        self.assertEqual(comment.user, self.ap_user)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)

    def test_supplier_invoice_edit_and_it_exists_a_new_comment(self):
        # Given an invoice and a logged Supplier
        # invoice : self.invoice
        self.client.force_login(self.user)
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
        comment = Comment.objects.filter(
            invoice = self.invoice
        ).latest('comment_date_received')

        self.assertEqual(
            str(comment),
            '{} has changed the invoice'.format(
                self.user.email,
            )
        )
        self.assertEqual(comment.user, self.user)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)

    @parameterized.expand([
        ('Valid text', HTTPStatus.FOUND),
    ])
    def test_ap_can_add_a_comment_in_an_invoice(self, message, expected_status_code):
        # Given an invoice and a logged AP
        # invoice : self.invoice
        self.client.force_login(self.ap_user)

        # When AP writes a comment
        response = self.client.post(
            reverse('post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {'message': message}
        )

        # Then the invoice should have a comment associated to it with its message
        comment = Comment.objects.filter(
            invoice = self.invoice
        ).latest('comment_date_received')

        self.assertEqual(expected_status_code, response.status_code)
        self.assertEqual(message, comment.message)
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
            reverse('post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {'message': message}
        )

        # Then the invoice should have a comment associated to it with its message
        comment = Comment.objects.filter(
            invoice = self.invoice
        ).latest('comment_date_received')

        self.assertEqual(expected_status_code, response.status_code)
        self.assertEqual(message, comment.message)
        self.assertEqual(comment.user, self.user)

    def test_post_an_empty_comment(self):
        # Given an invoice and a logged AP
        # invoice : self.invoice
        self.client.force_login(self.ap_user)

        # When AP writes an empty comment
        response = self.client.post(
            reverse('post-comment',
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
            reverse('post-comment',
                kwargs={
                    'pk': self.invoice.id,
                },
            ),
            {'message': message}
        )

        # Then the invoice should have a comment associated to it with its message
        comment = Comment.objects.filter(
            invoice = self.invoice
        ).latest('comment_date_received')

        self.assertEqual(expected_status_code, response.status_code)
        self.assertEqual(message, comment.message)
        self.assertEqual(comment.user, self.user)

    def test_comment_to_an_invoice_not_of_the_company(self):
        # Given an invoice and user (supplier)
        # from other taxpayer but from other company
        self.client.force_login(self.user)

        # When the user posts a comment
        response = self.client.post(
            reverse('post-comment',
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
            reverse('post-comment',
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
            reverse('post-comment',
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
                self.invoice.id
            )
        )
