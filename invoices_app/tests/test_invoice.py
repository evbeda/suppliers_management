from datetime import date, timedelta
from http import HTTPStatus
from parameterized import parameterized

from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.core import mail

from supplier_app.tests.factory_boy import CompanyUserPermissionFactory
from users_app.factory_boy import UserFactory

from invoices_app import (
    INVOICE_STATUS_APPROVED,
    INVOICE_STATUS_NEW,
    INVOICE_STATUS_REJECTED,
    INVOICE_STATUS_CHANGES_REQUEST,
    INVOICE_STATUS_PAID,
)
from invoices_app.factory_boy import InvoiceFactory
from invoices_app.forms import InvoiceForm
from invoices_app.models import Invoice
from invoices_app.tests.test_base import TestBase

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
        self.assertEqual(invoice.status, invoice_status_lookup(INVOICE_STATUS_NEW))

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
        (INVOICE_STATUS_APPROVED,),
        (INVOICE_STATUS_CHANGES_REQUEST,),
        (INVOICE_STATUS_REJECTED),
        (INVOICE_STATUS_PAID,),
    ])
    def test_invoice_change_status_in_db(self, status):
        self.client.force_login(self.ap_user)
        self.client.post(
            reverse(
                'change-invoice-status',
                kwargs={
                    'pk': self.invoice.id,
                }
            ),
            {'status': invoice_status_lookup(status),}
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
                'status': invoice_status_lookup(INVOICE_STATUS_APPROVED),
            }
        )
        self.assertEqual(request.status_code, expected)

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
            self.invoice_post_data
        )
        self.assertEqual(res.status_code, HTTPStatus.FOUND)
        self.invoice.refresh_from_db()
        self.assertEqual(
            self.invoice.invoice_number,
            self.invoice_post_data['invoice_number']
        )
        self.assertEqual(
            self.invoice.status,
            invoice_status_lookup(INVOICE_STATUS_NEW)
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

    def test_supplier_invoice_edit_permissions(self):
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

    def test_ap_invoice_edit_permissions(self):
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

    def test_suplier_invoice_detail_view_address(self):
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
            '{}?{}'.format(reverse('invoices-list'), 'taxpayer={}'.format(self.taxpayer.id))
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

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 3)

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
