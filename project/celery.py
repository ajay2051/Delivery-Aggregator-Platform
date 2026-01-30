import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# You don't need both autodiscover_tasks() and explicit app list
# Remove this line or use it instead of the above:
# app.autodiscover_tasks(['f1_auth'])  # Just the app name, not the module

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# Fix the export - should match your variable name
celery_app = app  # Create alias for consistency
__all__ = ["app", "celery_app"]
