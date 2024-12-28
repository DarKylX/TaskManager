from datetime import timedelta
from django.utils import timezone
from .models import (
    UserProfile,
    Task,
)  # локальные модули
from django.core.mail import send_mail
from celery import shared_task
from django.conf import settings

@shared_task
def delete_expired_tasks():
    expiration_date = timezone.now().date() - timedelta(days=30)
    Task.objects.filter(status__in=["BACKLOG", "IN_PROGRESS"], due_date__lt=expiration_date).delete()

@shared_task
def send_task_reminders():
    # Get tasks that need reminders
    tasks_due_soon = Task.objects.filter(
        due_date__lte=timezone.now() + timezone.timedelta(days=1),
        status='PENDING'
    )

    for task in tasks_due_soon:
        send_mail(
            subject=f'Reminder: Task "{task.title}" is due soon',
            message=f'Your task "{task.title}" is due {task.due_date}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.user.email],
            fail_silently=False,
        )

    return len(tasks_due_soon)  # Return number of reminders sent

@shared_task
def archive_completed_tasks():
    Task.objects.filter(status="DONE").update(category="Archived")

@shared_task
def delete_inactive_users():
    six_months_ago = timezone.now() - timedelta(days=180)
    UserProfile.objects.filter(last_login__lt=six_months_ago, is_staff=False).delete()
