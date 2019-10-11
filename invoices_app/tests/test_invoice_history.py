from django.urls import reverse

from invoices_app.models import Invoice
from invoices_app.views import invoice_history_changes
from supplier_management_site.tests.test_base import TestBase


class TestInvoiceHistory(TestBase):

    def test_history_changes_diff(self):
        self.invoice.po_number = '4321'
        self.invoice.save()
        history = Invoice.history.filter(id=self.invoice.id)
        self.assertEqual(
            invoice_history_changes(history.last()),
            [{'field': 'po_number', 'old': '98876', 'new': '4321'}]
        )

    def test_history_invoices_view(self):

        old_po_number = self.invoice.po_number
        self.invoice.po_number = '4321'
        new_po_number = self.invoice.po_number
        self.invoice.save()
        response = self.client.get(
            reverse('invoice-history', kwargs={'pk': self.invoice.id}),
        )
        self.assertContains(response, old_po_number)
        self.assertContains(response, new_po_number)
