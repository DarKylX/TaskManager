from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем настройки Django для Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TaskManager.settings")

app = Celery("TaskManager")

# Используем настройки Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматическое обнаружение задач
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
