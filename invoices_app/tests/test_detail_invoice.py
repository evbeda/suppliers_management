from http import HTTPStatus

from django.http import HttpResponseRedirect
from django.urls import reverse

from invoices_app.models import Invoice
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
        self.assertEqual(
            response.url,
            '/?next=/users/taxpayer/{}/invoice/{}/'.format(
                self.invoice.taxpayer.id,
                self.invoice.id
            ),
        )

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
        self.assertEqual(
            response.url,
            '/?next=/users/taxpayer/{}/invoice/{}/'.format(
                self.invoice_from_other_user.taxpayer.id,
                self.invoice_from_other_user.id
            ),
        )

    def test_get_detail_invoice_with_new_comment(self):
        self.client.force_login(self.ap_user)
        self.invoice.new_comment_from_supplier = True
        self.invoice.save()

        self.client.get(
            reverse(
                'invoices-detail',
                kwargs={
                    'taxpayer_id': self.invoice.taxpayer.id,
                    'pk': self.invoice.id,
                }
            )
        )
        self.assertFalse(Invoice.objects.filter(pk=self.invoice.id).last().new_comment_from_supplier)
