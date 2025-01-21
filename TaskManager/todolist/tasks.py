""" Периодичесукие задачи """
import json
import logging

from celery import shared_task
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import timedelta
from django_redis import get_redis_connection

from .models import Task, UserProfile, UserPageVisit  # локальные модули

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
    """Отправляет письма о сроке выполнения задач, которые наступят в течение дня"""
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
    """Архивирует завершенные задачи"""
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
    """Удаляет пользователей, которые не входили в систему за последние 6 месяцев"""
    six_months_ago = timezone.now() - timedelta(days=180)
    UserProfile.objects.filter(last_login__lt=six_months_ago, is_staff=False).delete()


@shared_task
def process_page_visits():
    redis_client = get_redis_connection("default")
    visits_to_create = []

    while True:
        # Используем Redis клиент напрямую вместо cache
        raw_visit = redis_client.rpop('page_visits')
        if not raw_visit:
            break

        try:
            # Для Redis версии 3+ нужно декодировать bytes в строку
            if isinstance(raw_visit, bytes):
                raw_visit = raw_visit.decode('utf-8')

            visit_data = json.loads(raw_visit)

            visits_to_create.append(UserPageVisit(
                user_id=visit_data['user_id'],
                path=visit_data['path'],
                ip_address=visit_data['ip_address']
            ))

            # Записываем батчами по 100 записей
            if len(visits_to_create) >= 100:
                UserPageVisit.objects.bulk_create(visits_to_create)
                visits_to_create = []

        except Exception as e:
            print(f"Error processing visit: {e}")

    # Записываем оставшиеся записи
    if visits_to_create:
        UserPageVisit.objects.bulk_create(visits_to_create)


# tasks.py
@shared_task
def cleanup_old_visits():
    from django.conf import settings
    from django.utils import timezone
    from django.db import connection

    retention_days = settings.PAGEVISITS_SETTINGS['RETENTION_DAYS']
    max_records = settings.PAGEVISITS_SETTINGS['MAX_RECORDS']
    batch_size = settings.PAGEVISITS_SETTINGS['CLEANUP_BATCH_SIZE']

    # Удаляем старые записи
    cutoff_date = timezone.now() - timezone.timedelta(days=retention_days)
    UserPageVisit.objects.filter(visited_at__lt=cutoff_date).delete()

    # Проверяем общее количество записей
    total_records = UserPageVisit.objects.count()
    if total_records > max_records:
        # Находим ID, после которого нужно удалить записи
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM todolist_userpagevisit 
                ORDER BY visited_at DESC 
                OFFSET %s LIMIT 1
            """, [max_records])
            cutoff_id = cursor.fetchone()[0]

        # Удаляем записи пакетами
        while True:
            deleted_count = UserPageVisit.objects.filter(
                id__lt=cutoff_id
            )[:batch_size].delete()[0]
            if deleted_count == 0:
                break

    return {
        'cleaned_before': cutoff_date,
        'total_records': UserPageVisit.objects.count()
    }
