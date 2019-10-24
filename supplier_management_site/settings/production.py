from .base import *  # noqa
import dj_database_url
from utils.env import get_env_variable

ALLOWED_HOSTS = [
    'britesu.herokuapp.com',
    'brite-su-qa.herokuapp.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'supplier_management_site',
        'USER': 'name',
        'PASSWORD': '',
        'PORT': '',
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static_prod')

SOCIAL_AUTH_EVENTBRITE_KEY = get_env_variable('SOCIAL_AUTH_EVENTBRITE_KEY')
SOCIAL_AUTH_EVENTBRITE_SECRET = get_env_variable(
   'SOCIAL_AUTH_EVENTBRITE_SECRET'
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = get_env_variable('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = get_env_variable(
   'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'
)

INSTALLED_APPS += [  # noqa
    'whitenoise.runserver_nostatic'
]

MIDDLEWARE += [  # noqa
    'whitenoise.middleware.WhiteNoiseMiddleware'
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.dropbox.DropBoxStorage'
DROPBOX_OAUTH2_TOKEN = get_env_variable('DROPBOX_OAUTH2_TOKEN')

DB_FROM_ENV = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(DB_FROM_ENV)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'testlogger': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    }
}

DEBUG_PROPAGATE_EXCEPTIONS = True

DEBUG = False

# EMAIL NOTIFICATION URLS
COMPANY_INVITATION_URL = os.environ.get('COMPANY_INVITATION_URL')
SUPPLIER_HOME_URL = os.environ.get('SUPPLIER_HOME_URL')

# CELERY REDIS CONFIG
BROKER_URL = 'redis://:{}@{}'.format(get_env_variable('REDISLAB_PASSWORD'), get_env_variable('REDISLAB_ENDPOINT'))
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_BROKER_URL = BROKER_URL
CELERY_RESULT_BACKEND = BROKER_URL
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
CELERY_EMAIL_TASK_CONFIG = {
    'name': 'djcelery_email_send',
    'ignore_result': True,
}
