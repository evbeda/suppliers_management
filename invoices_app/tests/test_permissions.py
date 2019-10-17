from parameterized import parameterized
from django.contrib.auth.models import Group

from users_app.factory_boy import UserFactory
from invoices_app.tests.test_base import TestBase
from invoices_app.views import (
    InvoiceDetailView,
    InvoiceHistory,
    InvoiceListView,
    InvoiceUpdateView,
    SupplierInvoiceCreateView,
    SupplierInvoiceListView,
)
from users_app import (
    CAN_VIEW_INVOICES_PERM,
    CAN_VIEW_INVOICES_HISTORY_PERM,
    CAN_EDIT_INVOICES_PERM,
    CAN_CREATE_INVOICE_PERM,
    CAN_VIEW_SUPPLIER_INVOICES_PERM,
)
from users_app.views import AdminList


class TestPermissions(TestBase):

    @parameterized.expand([
        (InvoiceListView, CAN_VIEW_INVOICES_PERM),
        (SupplierInvoiceListView, CAN_VIEW_SUPPLIER_INVOICES_PERM),
        (SupplierInvoiceCreateView, CAN_CREATE_INVOICE_PERM),
        (InvoiceUpdateView, CAN_EDIT_INVOICES_PERM),
        (InvoiceHistory, CAN_VIEW_INVOICES_HISTORY_PERM),
        (InvoiceDetailView, CAN_VIEW_INVOICES_PERM),
    ])
    def test_view_permission(self, view, permission):
        self.assertIn(permission, view.permission_required)

    @parameterized.expand([
        (InvoiceDetailView, True),
        (InvoiceHistory, True),
        (InvoiceListView, True),
        (InvoiceUpdateView, True),
        (SupplierInvoiceCreateView, False),
        (SupplierInvoiceListView, False),
    ])
    def test_ap_permissions(self, view, has_access):
        self.assertEqual(self.ap_user.has_perm(view.permission_required), has_access)

    @parameterized.expand([
        (InvoiceDetailView, True),
        (InvoiceHistory, False),
        (InvoiceListView, True),
        (InvoiceUpdateView, True),
        (SupplierInvoiceCreateView, True),
        (SupplierInvoiceListView, True),
    ])
    def test_supplier_user_permissions(self, view, has_access):
        self.assertEqual(self.user.has_perm(view.permission_required), has_access)

    @parameterized.expand([
        (InvoiceDetailView, True),
        (InvoiceHistory, False),
        (InvoiceListView, True),
        (InvoiceUpdateView, False),
        (SupplierInvoiceCreateView, False),
        (SupplierInvoiceListView, False),
    ])
    def test_reporter_user_permissions(self, view, has_access):
        user = UserFactory()
        reporter_group = Group.objects.get(name='ap_reporter')
        user.groups.add(reporter_group)
        self.assertEqual(user.has_perm(view.permission_required), has_access)

    @parameterized.expand([
        (InvoiceDetailView, False),
        (InvoiceHistory, False),
        (InvoiceListView, False),
        (InvoiceUpdateView, False),
        (SupplierInvoiceCreateView, False),
        (SupplierInvoiceListView, False),
        (AdminList, True),
    ])
    def test_manager_user_permissions(self, view, has_access):
        user = UserFactory()
        manager_group = Group.objects.get(name='ap_manager')
        user.groups.add(manager_group)
        self.assertEqual(user.has_perm(view.permission_required), has_access)
