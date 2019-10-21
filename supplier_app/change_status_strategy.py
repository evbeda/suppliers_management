from utils.send_email import taxpayer_notification


class StrategyStatusChange():
    def send_email(taxpayer):
        raise NotImplementedError()

    def change_taxpayer_status(taxpayer):
        raise NotImplementedError()


class StrategyDeny(StrategyStatusChange):

    def send_email(taxpayer):
        taxpayer_notification(taxpayer, 'taxpayer_denial')

    def change_taxpayer_status(taxpayer):
        taxpayer.deny_taxpayer()
        taxpayer.save()


class StrategyApprove(StrategyStatusChange):

    def send_email(taxpayer):
        taxpayer_notification(taxpayer, 'taxpayer_approval')

    def change_taxpayer_status(taxpayer):
        taxpayer.approve_taxpayer()
        taxpayer.save()


strategy = {
    "approve": StrategyApprove,
    "deny": StrategyDeny,
}


def get_strategy(action):
    return strategy[action]
