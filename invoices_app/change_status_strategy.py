from django.core.validators import validate_integer
from django.db import IntegrityError
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from invoices_app import (
    INVOICE_STATUS_APPROVED_CODE,
    INVOICE_STATUS_CHANGES_REQUEST_CODE,
    INVOICE_STATUS_PAID_CODE,
    INVOICE_STATUS_PENDING_CODE,
    INVOICE_STATUS_REJECTED_CODE,
    NO_COMMENT_ERROR,
    NO_WORKDAY_ID_ERROR,
    INVOICE_STATUS_IN_PROGRESS_CODE)
from invoices_app.models import Invoice
from supplier_app.exceptions.taxpayer_exceptions import TaxpayerUniqueWorkdayId


def change_status(invoice, status, *args):
    invoice.status = status


def strategy_change_to_in_progress(invoice, status, request):
    change_status(invoice, status)
    workday_id = request.POST.get('workday_id')
    if not workday_id:
        raise ValidationError(NO_WORKDAY_ID_ERROR)
    if Invoice.objects.filter(workday_id=workday_id).exists():
        raise IntegrityError(_("Workday ID already exist"))
    invoice.workday_id = workday_id


def strategy_change_to_changes_requested(invoice, status, request):
    change_status(invoice, status)
    message = request.POST.get('message')
    if not message:
        raise ValidationError(NO_COMMENT_ERROR)
    invoice.changeReason = message


def get_change_status_strategy(status):
    strategy_assignment = {
        INVOICE_STATUS_APPROVED_CODE: change_status,
        INVOICE_STATUS_CHANGES_REQUEST_CODE: strategy_change_to_changes_requested,
        INVOICE_STATUS_PAID_CODE: change_status,
        INVOICE_STATUS_PENDING_CODE: change_status,
        INVOICE_STATUS_REJECTED_CODE: change_status,
        INVOICE_STATUS_IN_PROGRESS_CODE: strategy_change_to_in_progress,
    }
    return strategy_assignment[status]
