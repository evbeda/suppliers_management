from django.utils.translation import ugettext_lazy as _

TRANSACTION_TYPE_AR = {
    _("Bank transfer"): 1
}

ACCOUNT_TYPE_AR = {
    _("Saving account"): 1,
    _("Checking account"): 2
}


def get_transaction_type_info_choices():
    return [(v, k) for k, v in TRANSACTION_TYPE_AR.items()]


def get_account_type_info_choices():
    return [(v, k) for k, v in ACCOUNT_TYPE_AR.items()]
