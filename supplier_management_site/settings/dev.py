from .base import * # noqa

from supplier_management_site import get_env_variable

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

SOCIAL_AUTH_EVENTBRITE_KEY = get_env_variable('SOCIAL_AUTH_EVENTBRITE_KEY')
SOCIAL_AUTH_EVENTBRITE_SECRET = get_env_variable(
   'SOCIAL_AUTH_EVENTBRITE_SECRET'
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DEBUG = True
