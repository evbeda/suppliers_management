worker: celery worker -A supplier_management_site --loglevel=debug -E
release: python manage.py migrate --run-syncdb
web: gunicorn supplier_management_site.wsgi --log-file -