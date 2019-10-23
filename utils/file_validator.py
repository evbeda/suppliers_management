from invoices_app import (
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
