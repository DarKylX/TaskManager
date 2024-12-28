from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

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

app.conf.beat_schedule = {
    'delete-expired-tasks': {
        'task': 'todolist.tasks.delete_expired_tasks',
        'schedule': crontab(hour='0', minute='0'),  # Каждый день в полночь
    },
    'send-task-reminders': {
        'task': 'todolist.tasks.send_task_reminders',
        'schedule': crontab(hour='1', minute='45'),  # Каждый день в 1:15
    },
    'archive-completed-tasks': {
        'task': 'todolist.tasks.archive_completed_tasks',
        'schedule': crontab(hour='1', minute='0'),  # Каждый день в 1:00
    },
    'delete-inactive-users': {
        'task': 'todolist.tasks.delete_inactive_users',
        'schedule': crontab(minute='0', hour='0', day_of_month='1'),  # Первый день каждого месяца
    },
}