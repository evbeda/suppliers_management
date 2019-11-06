from django.core.files import File
from unittest.mock import MagicMock

from supplier_app import (
    PAYMENT_TERMS,
    PAYMENT_TYPES,
)
from supplier_app.constants.bank_info import BANK_INFO

BUSINESS_EXAMPLE_NAME_1 = 'Pyme 1'
BUSINESS_EXAMPLE_NAME_2 = 'Pyme 2'

file_mock = MagicMock(spec=File)
file_mock.name = 'test.pdf'
file_mock.size = 50

STATUS_PENDING = "PENDING"
STATUS_ACTIVE = "ACTIVE"
STATUS_CHANGE_REQUIRED = "CHANGE REQUIRED"
STATUS_DENIED = "DENIED"

TOKEN_COMPANY = 'f360da6197be4436a4b686460289085c14a859d634a9daca2d7d137b178b193e'


def get_bank_info_example(key=None):
    return BANK_INFO[key or "BANCO DE LA NACION ARGENTINA"]


def get_payment_term_example(index=None):
    return PAYMENT_TERMS[index or 0].value


def get_payment_type_example(index=None):
    return PAYMENT_TYPES[index or 0].value


def taxpayer_creation_POST_factory(
    eb_entity=None,
    afip_file=None,
    witholding_taxes_file=None,
    bank_cbu_file=None,
    bank_info=None,
):
    return {
        'taxpayer_form-workday_id': '1',
        'taxpayer_form-business_name': 'EB ARG',
        'taxpayer_form-cuit': '20312321402',
        'taxpayer_form-country': 'AR',
        'taxpayer_form-eb_entities': eb_entity,
        'taxpayer_form-payment_type': 'BANK',
        'taxpayer_form-payment_term': '30',
        'taxpayer_form-afip_registration_file': afip_file or file_mock,
        'taxpayer_form-witholding_taxes_file': witholding_taxes_file or file_mock,
        'address_form-street': 'San Martin',
        'address_form-number': '21312',
        'address_form-zip_code': '123',
        'address_form-city': 'Mendoza',
        'address_form-state': 'Mendoza',
        'address_form-country': 'AR',
        'bank_account_form-bank_cbu_file': bank_cbu_file or file_mock,
        'bank_account_form-bank_info': bank_info or get_bank_info_example(),
        'bank_account_form-bank_account_number': '1113111162117111131111',
    }


def taxpayer_edit_POST_factory(
    eb_entity=None,
    business_name=None,
    cuit=None,
    payment_type=None,
    payment_term=None
):
    return {
            'business_name': business_name or 'EB ARG',
            'eb_entities': eb_entity or "1",
            'country': 'AR',
            'cuit': cuit or '12031232140',
            'payment_type': get_payment_type_example(payment_type),
            'payment_term': get_payment_term_example(payment_term),
            'afip_registration_file': file_mock,
            'witholding_taxes_file': file_mock,
    }
