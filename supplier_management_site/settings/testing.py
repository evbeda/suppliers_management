from .base import *  # noqa

SECRET_KEY = 'testpepe'
DEBUG = True

ALLOWED_HOSTS = [
    'testserver',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlitetesting3'),  # noqa
    }
}
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
