from .base import *  # noqa

DEBUG = True

ALLOWED_HOSTS = ['testserver']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlitetesting3'),
    }
}
