# 25 * 1014 * 1024
TAXPAYER_BANK_ACCOUNT_MAX_SIZE_FILE = 26214400

TAXPAYER_BANK_ACCOUNT_ALLOWED_FILE_EXTENSIONS = ['.pdf']

TAXPAYER_STATUS = {
    "ACTIVE": "Active",
    "CHANGE REQUIRED": "Change required",
    "PENDING": "Pending",
    "DENIED": "Denied",
}


def get_taxpayer_status_choices():
    return [(k, v) for k, v in TAXPAYER_STATUS.items()]


def get_taxpayer_status_pending_and_change_required():
    return [v for k, v in TAXPAYER_STATUS.items() if (k=="PENDING" or k=="CHANGE REQUIRED")] 
