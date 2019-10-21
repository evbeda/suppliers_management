import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supplier_management_site.settings')

celery_app = Celery('supplier_management_site')
celery_app.config_from_object('django.conf:settings')
celery_app.autodiscover_tasks(settings.INSTALLED_APPS)
