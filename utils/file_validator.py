def validate_file(file, max_size_form):
    return (True, '') \
        if file.size <= max_size_form \
        else (False, 'Your file is greater than {}.'.format(max_size_form))
