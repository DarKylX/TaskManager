""" Периодичесукие задачи """
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.timezone import timedelta
from .models import Task, UserProfile  # локальные модули

logger = logging.getLogger(__name__)
# pylint: disable=logging-fstring-interpolation


@shared_task
def delete_expired_tasks():
    """Удаляет завершенные и \
    незавершенные задачи, которые наступят в течение 30 дней """
    expiration_date = timezone.now().date() - timedelta(days=30)
    Task.objects.filter(
        status__in=["BACKLOG", "IN_PROGRESS"], due_date__lt=expiration_date
    ).delete()


@shared_task(bind=True)
def send_task_reminders(_self):
    """Отправляет письма о сроке выполнения задач, которые наступят в течение дня """
    # logger.info("Задача send_task_reminders начата")
    # print("Задача send_task_reminders начата")  # Для явного вывода

    try:
        # Получаем задачи, которые требуют напоминаний
        tasks_due_soon = Task.objects.filter(
            due_date=timezone.now() + timezone.timedelta(days=1)
        ).exclude(status="DONE")
        # logger.debug(f"Найдено задач для напоминаний: {tasks_due_soon.count()}")
        # print(f"Найдено задач для напоминаний: {tasks_due_soon.count()}")

        for task in tasks_due_soon:
            # pylint: disable=broad-exception-caught
            try:
                # logger.debug(f"Отправка письма для задачи: {task.name}")
                # print(f"Отправка письма для задачи: {task.name}")
                send_mail(
                    subject=f'Напоминание: \
                    Срок исполнения задачи "{task.name}" скоро истекает',
                    message=f'Ваша задача \
                    "{task.name}" должна быть выполнена до {task.due_date}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[task.assignee.email],
                    fail_silently=False,
                )
            #  logger.info(f"Письмо для задачи '{task.name}' успешно отправлено")
            except Exception as e:
                # logger.error \
                # (f"Ошибка при отправке письма для задачи '{task.name}': {e}")
                print(f"Ошибка при отправке письма для задачи '{task.name}': {e}")

        return tasks_due_soon.count()

    except Exception as e:
        logger.error(f"Ошибка в задаче send_task_reminders: {e}")
        print(f"Ошибка в задаче send_task_reminders: {e}")
        raise


@shared_task
def archive_completed_tasks():
    """Архивирует завершенные задачи """
    try:
        # Логирование начала выполнения задачи
        logger.info("Задача 'archive_completed_tasks' начата.")
        print("Задача 'archive_completed_tasks' начата.")

        # Отбор задач со статусом "DONE"
        completed_tasks = Task.objects.filter(status="DONE")
        logger.debug(f" {completed_tasks.count()} задач(а) со статусом 'DONE'.")
        print(f"{completed_tasks.count()} задач(а) со статусом 'DONE'.")

        # Обновление категории задач
        updated_count = completed_tasks.update(category="Archived")
        logger.info(f"У {updated_count} задач был изменен статус на 'Archived'.")
        print(f"У {updated_count} задач был изменен статус на  'Archived'.")

        # Возврат результата для мониторинга
        return updated_count

    except Exception as e:
        # Логирование ошибок
        logger.error(f"Error in 'archive_completed_tasks': {e}")
        print(f"Error in 'archive_completed_tasks': {e}")
        raise


@shared_task
def delete_inactive_users():
    """Удаляет пользователей, которые не входили в систему за последние 6 месяцев """
    six_months_ago = timezone.now() - timedelta(days=180)
    UserProfile.objects.filter(last_login__lt=six_months_ago, is_staff=False).delete()
