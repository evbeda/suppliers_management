from invoices_app import (
    INVOICE_FILE_FIELDS,
    INVOICE_MAX_SIZE_FILE,
    INVOICE_ALLOWED_FILE_EXTENSIONS,
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



def is_file_valid(self, valid, file_field):
    if not valid:
        return valid
    for file_field in INVOICE_FILE_FIELDS:
        file_data = self.cleaned_data[file_field]
        if file_data:
            file_is_valid, msg = validate_file(
                file_data,
                INVOICE_MAX_SIZE_FILE,
            )
            if not file_is_valid:
                self.add_error(file_field, msg)
                return file_is_valid
    return valid
