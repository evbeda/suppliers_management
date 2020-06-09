from django.utils.translation import ugettext_lazy as _

TRANSACTION_TYPE_USA = {
    _("Check"): 1,
    _("ACH"): 1,
    _("Wire"): 1,
}

ACCOUNT_TYPE_USA = {
    _("Saving account"): 1,
    _("Checking account"): 2
}


def get_transaction_type_usa_info_choices():
    return [(v, k) for k, v in TRANSACTION_TYPE_USA.items()]


def get_account_type_info_usa_choices():
    return [(v, k) for k, v in ACCOUNT_TYPE_USA.items()]