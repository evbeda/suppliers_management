from django.core.exceptions import ValidationError

from django.utils.translation import ugettext_lazy as _
from django.utils.deconstruct import deconstructible

from invoices_app import (
    INVOICE_MAX_SIZE_FILE,
    INVOICE_ALLOWED_FILE_EXTENSIONS,
)


@deconstructible
class FileSizeValidator(object):

    message = _("File size {}MB is not allowed.\n Limit size: {}MB.")
    divisor = 1048576

    code = 'invalid_size'

    def __init__(self, limit_size=None, message=None, code=None):
        self.limit_size = limit_size
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        size = value.size
        if self.limit_size is not None and size > self.limit_size:
            raise ValidationError(
                self.message.format(int(size/self.divisor), int(self.limit_size/self.divisor)),
                code=self.code,
                params={
                    'size': size,
                    'limit_size': ', '.join(str(self.limit_size))
                }
            )


def validate_file(file, max_size_form=None):
    if not max_size_form:
        max_size_form = INVOICE_MAX_SIZE_FILE

    value_to_return = {'is_valid': True, "errors": []}
    valid_content_type = False

    if file.size >= max_size_form:
        value_to_return['is_valid'] = False
        value_to_return['errors'].append(
            'The file size is greater than {}MB.'.format(int(max_size_form/(1024*1024)))
        )

    for i in INVOICE_ALLOWED_FILE_EXTENSIONS:
        if file.name.endswith(i):
            valid_content_type = True

    if not valid_content_type:
        value_to_return['is_valid'] = False
        value_to_return['errors'].append(
            'Only {} allowed'.format(
                ''.join(INVOICE_ALLOWED_FILE_EXTENSIONS)
            )
        )
    return list(value_to_return.values())
