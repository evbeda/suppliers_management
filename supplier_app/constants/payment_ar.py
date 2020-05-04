PAYMENT_TYPE_AR = {
    'Transferencia': 1
}

ACCOUNT_TYPE_AR = {
    'Caja de Ahorro': 1,
    'Cuenta corriente': 2
}


def get_payment_type_info_choices():
    return [(v, k) for k, v in PAYMENT_TYPE_AR.items()]


def get_account_type_info_choices():
    return [(v, k) for k, v in ACCOUNT_TYPE_AR.items()]
