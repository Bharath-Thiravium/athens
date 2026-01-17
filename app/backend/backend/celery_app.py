import os
from celery import Celery

# Point Celery at Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")

# Use Redis as broker explicitly
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
