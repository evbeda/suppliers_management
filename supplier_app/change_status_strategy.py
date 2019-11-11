from django.contrib import messages

from supplier_app.models import TaxPayer

from supplier_app.constants.taxpayer_status import (
    TAXPAYER_STATUS_APPROVED,
    TAXPAYER_STATUS_CHANGE_REQUIRED,
    TAXPAYER_STATUS_DENIED,
)
from supplier_app.exceptions.taxpayer_exceptions import (
    NoWorkdayIDException,
    TaxpayerUniqueWorkdayId,
)
from supplier_app.constants.custom_messages import (
    TAXPAYER_APPROVE_MESSAGE,
    TAXPAYER_DENIED_MESSAGE,
    TAXPAYER_REQUEST_CHANGE_MESSAGE,
)
from utils.send_email import taxpayer_notification


def _taxpayer_exists_with_workday_id(workday_id):

    if TaxPayer.objects.filter(workday_id=workday_id).exists():
        raise TaxpayerUniqueWorkdayId()


class StrategyStatusChange():
    def send_email(taxpayer):
        raise NotImplementedError()

    def change_taxpayer_status(taxpayer, request):
        raise NotImplementedError()

    def show_message(request):
        raise NotImplementedError()


class StrategyDeny(StrategyStatusChange):

    def send_email(taxpayer):
        taxpayer_notification(taxpayer, 'taxpayer_denial')

    def change_taxpayer_status(taxpayer, request=None):
        taxpayer.deny_taxpayer()
        taxpayer.save()

    def show_message(request):
        messages.success(request, TAXPAYER_DENIED_MESSAGE)


class StrategyApprove(StrategyStatusChange):

    def send_email(taxpayer):
        taxpayer_notification(taxpayer, 'taxpayer_approval')

    def change_taxpayer_status(taxpayer, request=None):
        try:
            workday_id = request.POST['workday_id']
            _taxpayer_exists_with_workday_id(workday_id)
            if workday_id == "" and not taxpayer.workday_id:
                raise NoWorkdayIDException()
            taxpayer.workday_id = workday_id or taxpayer.workday_id
        except KeyError:
            raise NoWorkdayIDException()
        taxpayer.approve_taxpayer()
        taxpayer.save()

    def show_message(request):
        messages.success(request, TAXPAYER_APPROVE_MESSAGE)


class StrategyChangeRequired(StrategyStatusChange):

    def send_email(taxpayer):
        taxpayer_notification(taxpayer, 'taxpayer_change_required')

    def change_taxpayer_status(taxpayer, request=None):
        taxpayer.change_required_taxpayer()
        taxpayer.save()

    def show_message(request):
        messages.success(request, TAXPAYER_REQUEST_CHANGE_MESSAGE)


strategy = {
    TAXPAYER_STATUS_APPROVED: StrategyApprove,
    TAXPAYER_STATUS_CHANGE_REQUIRED: StrategyChangeRequired,
    TAXPAYER_STATUS_DENIED: StrategyDeny,
}


def run_strategy_taxpayer_status(action, taxpayer, request):
    strategy_type = strategy[action]
    strategy_type.change_taxpayer_status(taxpayer, request)
    strategy_type.send_email(taxpayer)
    strategy_type.show_message(request)
