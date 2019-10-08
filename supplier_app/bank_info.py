BANK_INFO = {
    "CITIBANK N.A.": 16,
    "BANCO DE GALICIA Y BUENOS AIRES S.A.": 7,
    "BANCO DE LA NACION ARGENTINA": 11,
    "BBVA BANCO FRANCES S.A.": 17,
}


def get_bank_info_choices():
    return [(v, k) for k, v in BANK_INFO.items()]
