from http import HTTPStatus
from parameterized import parameterized

from django.urls import reverse
from django.shortcuts import get_object_or_404

from invoices_app import (
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_NEW,
    INVOICE_STATUS_REJECTED,
    INVOICE_STATUS_CHANGES_REQUEST
)
from invoices_app.factory_boy import InvoiceFactory
from invoices_app.forms import InvoiceForm
from invoices_app.models import Invoice
from invoices_app.tests.test_base import TestBase


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
        self.file_mock.name = name_file
        self.file_mock.size = size_file
        form = InvoiceForm(
            data=self.invoice_post_data,
            files={
                'invoice_file': self.file_mock,
            }
        )
        self.assertEqual(form.is_valid(), expected)

    @parameterized.expand([
        ('test.pdf', 20, True),
        ('test.xml', 20, False),
        ('test.pdf', 500000000, False),
        ('test.xml', 500000000, False),

    ])
    def test_form_po_file_is_valid(self, name_file, size_file, expected):
        self.po_file_mock.name = name_file
        self.po_file_mock.size = size_file
        form = InvoiceForm(
            data=self.invoice_post_data,
            files={
                'invoice_file': self.file_mock,
                'po_file': self.po_file_mock,
            }
        )
        self.assertEqual(form.is_valid(), expected)

    def test_invoice_create_db(self):
        self.assertEqual(
            Invoice.objects.get(invoice_number='1234'),
            self.invoice_creation_valid_data
        )

    def test_invoice_create_view(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('invoice-create', kwargs={'taxpayer_id': self.taxpayer.id}),
            self.invoice_post_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        invoice = Invoice.objects.get(invoice_number=self.invoice_post_data['invoice_number'])
        self.assertEqual(invoice.status, INVOICE_STATUS_NEW)

    def test_invoice_create_existing_invoice_id(self):
        self.client.force_login(self.user)
        self.invoice_post_data['invoice_number'] = self.invoice_creation_valid_data.invoice_number
        response = self.client.post(
            reverse('invoice-create', kwargs={'taxpayer_id': self.taxpayer.id}),
            self.invoice_post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response,
            'The invoice {} already exists'.format(self.invoice_creation_valid_data.invoice_number)
        )

    def test_supplier_invoices_list_view(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('supplier-invoice-list', kwargs={'taxpayer_id': self.taxpayer.id}),
        )
        self.assertContains(response, self.invoice_creation_valid_data.po_number)
        self.assertContains(response, self.invoice_creation_valid_data.status)

    def test_supplier_invoices_list_only_taxpayer_invoices(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('supplier-invoice-list', kwargs={'taxpayer_id': self.taxpayer.id}),
        )
        # Only the invoice with from the tax payer should be listed.
        self.assertIn(
            self.invoice_creation_valid_data.taxpayer.id,
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
        # Only the invoice with from the tax payer should be listed.
        self.assertIn(
            self.invoice_creation_valid_data.taxpayer.id,
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
        (INVOICE_STATUS_APPROVED),
        (INVOICE_STATUS_NEW),
        (INVOICE_STATUS_REJECTED),
        (INVOICE_STATUS_CHANGES_REQUEST),
    ])
    def test_invoice_change_status_in_db(self, status):
        self.client.force_login(self.ap_user)
        self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': self.invoice_creation_valid_data.id,
                }
            ),
            {
            'status': status,
            }
        )
        invoice = get_object_or_404(Invoice, pk=self.invoice_creation_valid_data.id)
        self.assertEqual(invoice.status, status)

    def test_invoice_change_status_not_in_available_status(self):
        self.client.force_login(self.ap_user)
        request = self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': self.invoice_creation_valid_data.id,
                }
            ),
            {
            'status': 'NOT_STATUS',
            }
        )
        self.assertEqual(request.status_code, 400)

    def test_invoice_change_status_only_ap_fail(self):
        self.client.force_login(self.user)
        request = self.client.post(
            reverse(
                'change-invoice-status', 
                kwargs={
                    'pk': self.invoice_creation_valid_data.id,
                }
            ),
            {
            'status': INVOICE_STATUS_APPROVED,
            }
        )
        self.assertEqual(request.status_code, HTTPStatus.FORBIDDEN)
        
    @parameterized.expand([
        (1, 302),
        (31, 404),
        (1, 302),
        (31, 404),
    ])
    def test_invoice_change_status_code(self, id, expected):
        self.client.force_login(self.ap_user)
        request = self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': id,
                }
            ),
            {
                'status': INVOICE_STATUS_APPROVED,
            }
        )
        self.assertEqual(request.status_code, expected)

    def test_supplier_invoice_edit(self):
        self.client.force_login(self.user)
        self.invoice_creation_valid_data.status = INVOICE_STATUS_CHANGES_REQUEST
        self.invoice_creation_valid_data.save()
        res = self.client.post(
            reverse(
                'taxpayer-invoice-update',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice_creation_valid_data.id
                }
            ),
            self.invoice_post_data
        )
        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.invoice_creation_valid_data.refresh_from_db()
        self.assertEqual(
            self.invoice_creation_valid_data.invoice_number,
            self.invoice_post_data['invoice_number']
        )

    def test_supplier_invalid_invoice_edit_request(self):
        self.client.force_login(self.user)
        self.invoice_creation_valid_data.status = INVOICE_STATUS_CHANGES_REQUEST
        self.invoice_creation_valid_data.save()

        old_invoice_number = self.invoice_creation_valid_data.invoice_number
        res = self.client.post(
            reverse(
                'taxpayer-invoice-update',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice_creation_valid_data.id
                }
            ),
            {}
        )
        self.assertEqual(res.status_code, HTTPStatus.OK)
        self.invoice_creation_valid_data.refresh_from_db()
        self.assertEqual(
            self.invoice_creation_valid_data.invoice_number,
            old_invoice_number
        )
        self.assertContains(res, 'This field is required.')

    def test_supplier_invoice_edit_permissions(self):
        self.client.force_login(self.user)

        self.invoice_creation_valid_data.status = INVOICE_STATUS_CHANGES_REQUEST
        self.invoice_creation_valid_data.save()
        res = self.client.post(
            reverse(
                'taxpayer-invoice-update',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice_creation_valid_data.id
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

    def test_ap_invoice_edit_permissions(self):
        self.client.force_login(self.ap_user)
        self.invoice_creation_valid_data.status = INVOICE_STATUS_APPROVED
        self.invoice_creation_valid_data.save()
        res = self.client.post(
            reverse(
                'taxpayer-invoice-update',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice_creation_valid_data.id
                }
            ),
            self.invoice_post_data,
        )
        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.invoice_creation_valid_data.refresh_from_db()
        self.assertEqual(
            self.invoice_creation_valid_data.invoice_number,
            self.invoice_post_data['invoice_number']
        )

    def test_suplier_invoice_detail_view_address(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'invoices-detail',
                kwargs={
                    'taxpayer_id': self.taxpayer.id,
                    'pk': self.invoice_creation_valid_data.id
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
                    'pk': self.invoice_creation_valid_data.id
                }
            )
        )
        self.assertEqual(response.context['address'], self.address)
