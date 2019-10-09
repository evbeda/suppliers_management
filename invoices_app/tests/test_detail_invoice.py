from http import HTTPStatus
from parameterized import parameterized

from django.http import HttpResponseRedirect
from django.urls import reverse

from invoices_app import (
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_REJECTED,
    INVOICE_STATUS_CHANGES_REQUEST,
    INVOICE_STATUS_PAID,
)
from invoices_app.models import Comment
from invoices_app.tests.test_base import TestBase

class DetailInvoiceTest(TestBase):

    def test_click_in_row_invoice_redirects_to_detail_invoice(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('invoices-detail',
                    kwargs={
                        'taxpayer_id': self.invoice.taxpayer.id,
                        'pk': self.invoice.id,
                        }
                    ),
        )
        self.assertEqual(HTTPStatus.OK, response.status_code)

    def test_get_detail_invoice_without_login(self):
        response = self.client.get(
            reverse('invoices-detail',
                    kwargs={
                        'taxpayer_id': self.invoice.taxpayer.id,
                        'pk': self.invoice.id,
                        }
                    ),
        )
        self.assertEqual(type(response), HttpResponseRedirect)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(response.url, '/?next=/invoices/taxpayer/1/detail/1/')

    def test_get_detail_invoice_with_no_corresponding_supplier(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('invoices-detail',
                    kwargs={
                        'taxpayer_id': self.invoice_from_other_user.taxpayer.id,
                        'pk': self.invoice_from_other_user.id,
                        }
                    ),
        )

        self.assertEqual(type(response), HttpResponseRedirect)
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual(response.url, '/?next=/invoices/taxpayer/2/detail/2/')

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
            {'status': new_status}
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
        self.invoice.status = INVOICE_STATUS_CHANGES_REQUEST
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

    def test_ap_can_add_a_comment_in_an_invoice(self, message, expected_status_code):
        pass

    def test_a_valid_supplier_can_add_a_comment_in_an_invoice(self):
        pass

    def test_ap_can_add_a_comment_in_an_invoice(self):
        pass

    def test_a_no_valid_supplier_cannot_add_a_comment(self):
        pass

    def test_comments_are_chronologically_ordered(self):
        pass

    def test_ap_can_see_comments(self):
        pass

    def test_supplier_can_see_comments_of_his_invoices(self):
        pass

    def test_supplier_cannot_see_comments_of_other_invoices(self):
        pass
