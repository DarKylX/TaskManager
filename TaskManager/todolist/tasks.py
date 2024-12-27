from datetime import timedelta
from django.utils import timezone
from .models import (
    UserProfile,
    Task,
)  # локальные модули
from django.core.mail import send_mail
from celery import shared_task

@shared_task
def delete_expired_tasks():
    expiration_date = timezone.now().date() - timedelta(days=30)
    Task.objects.filter(status__in=["BACKLOG", "IN_PROGRESS"], due_date__lt=expiration_date).delete()

@shared_task
def send_task_reminders():
    tomorrow = timezone.now().date() + timedelta(days=1)
    tasks = Task.objects.filter(due_date=tomorrow)
    for task in tasks:
        if task.assignee and task.assignee.email:
            send_mail(
                'Напоминание о задаче',
                f'Напоминаем о задаче "{task.name}", крайний срок завтра.',
                'admin@example.com',
                [task.assignee.email],
            )

@shared_task
def archive_completed_tasks():
    Task.objects.filter(status="DONE").update(category="Archived")

@shared_task
def delete_inactive_users():
    six_months_ago = timezone.now() - timedelta(days=180)
    UserProfile.objects.filter(last_login__lt=six_months_ago, is_staff=False).delete()
