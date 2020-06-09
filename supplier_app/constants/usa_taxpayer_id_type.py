from django.utils.translation import ugettext_lazy as _

TAXPAYER_ID_TYPE = {
    "EIN": 1,
    "SSN": 2,
}


def get_usa_taxpayer_id_info_choices():
    return [(v, k) for k, v in TAXPAYER_ID_TYPE.items()]
