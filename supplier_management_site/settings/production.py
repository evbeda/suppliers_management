from .base import *
import dj_database_url


ALLOWED_HOSTS = ['secure-plateau-22734.herokuapp.com']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'supplier_management_site',
        'USER': 'name',
        'PASSWORD': '',
        'PORT': '',
    }
}

DB_FROM_ENV = dj_database_url.config(conn_max_age=500)

DATABASES['default'].update(DB_FROM_ENV)

DEBUG = True 
