from django.contrib import messages

from supplier_app.exceptions.taxpayer_exceptions import NoWorkdayIDException
from supplier_app.constants.custom_messages import (
    TAXPAYER_APPROVE_MESSAGE,
    TAXPAYER_DENIED_MESSAGE,
    TAXPAYER_REQUEST_CHANGE_MESSAGE,
)
from utils.send_email import taxpayer_notification



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
            taxpayer.workday_id = workday_id
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
    "approve": StrategyApprove,
    "deny": StrategyDeny,
}


def get_strategy(action):
    return strategy[action]
