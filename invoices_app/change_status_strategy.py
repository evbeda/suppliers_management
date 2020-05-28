from django.core.validators import validate_integer
from django.forms import ValidationError

from invoices_app import (
    INVOICE_STATUS_APPROVED_CODE,
    INVOICE_STATUS_CHANGES_REQUEST_CODE,
    INVOICE_STATUS_PAID_CODE,
    INVOICE_STATUS_PENDING_CODE,
    INVOICE_STATUS_REJECTED_CODE,
    NO_COMMENT_ERROR,
    NO_WORKDAY_ID_ERROR,
    INVOICE_STATUS_IN_PROGRESS_CODE)


def change_status(invoice, status, *args):
    invoice.status = status


def strategy_change_to_in_progress(invoice, status, request):
    change_status(invoice, status)
    workday_id = request.POST.get('workday_id')
    if not workday_id:
        raise ValidationError(NO_WORKDAY_ID_ERROR)
    validate_integer(workday_id)
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
