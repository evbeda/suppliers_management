from .base import *  # noqa

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlitetesting3'),
    }
}

SOCIAL_AUTH_EVENTBRITE_KEY = "pepe"
SOCIAL_AUTH_EVENTBRITE_SECRET = "pepe"
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = "pepe"
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = "pepe"
