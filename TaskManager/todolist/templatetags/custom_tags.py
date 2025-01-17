from django import template
from django.db.models import Count
from django.utils import timezone
from ..models import Task, Project

register = template.Library()


@register.simple_tag
def count_tasks_by_status(status_display, user):
    """
    Подсчитывает количество задач для определенного статуса
    status_display - отображаемое имя статуса (например "В работе")
    """
    # Получаем словарь статусов в обратном порядке (имя: код) # k = "NEW", v = "Новая"
    status_dict = {v: k for k, v in Task.STATUS_CHOICES}
#     status_dict = {
#     "Новая": "NEW",
#     "В работе": "IN_PROGRESS",
#     "Завершена": "DONE"
# }
    # Получаем код статуса по отображаемому имени
    # Например, если status_display = "В работе" ернет "IN_PROGRESS"
    status_code = status_dict.get(status_display)

    if status_code:
        count = Task.objects.filter(status=status_code, assignee=user).count()

        # Определяем правильное окончание
        if count % 10 == 1 and count % 100 != 11:
            word = "задача"
        elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
            word = "задачи"
        else:
            word = "задач"

        return f"{count} {word}"
    return "0 задач"


@register.simple_tag
def get_overdue_tasks(user):
    """Возвращает просроченные задачи пользователя"""
    return Task.objects.filter(
        assignee=user,
        due_date__lt=timezone.now().date(),
        status__in=['NEW', 'BACKLOG', 'IN_PROGRESS']
    )


@register.filter
def days_overdue(due_date):
    """
    Возвращает количество дней просрочки с правильным склонением слова 'день'
    """
    if not due_date:
        return "срок не указан"

    today = timezone.now().date()
    days = (today - due_date).days

    if days <= 0:
        return "не просрочено"

    # Склонение слова "день"
    if days % 10 == 1 and days % 100 != 11:
        day_word = "день"
    elif 2 <= days % 10 <= 4 and (days % 100 < 10 or days % 100 >= 20):
        day_word = "дня"
    else:
        day_word = "дней"

    return f"Просрочено на {days} {day_word}"


@register.inclusion_tag('dashboard/project_stats.html', takes_context=True)
def show_project_stats(context):
    """
    Показывает статистику по проектам пользователя
    """
    user = context['request'].user
    projects = Project.objects.filter(members=user)

    stats = {
        'total_projects': projects.count(),
        'active_projects': projects.filter(status__in=["NEW", "IN_PROGRESS"]).count(),
        'completed_projects': projects.filter(status='DONE').count(),
        'total_tasks': Task.objects.filter(project__in=projects).count(),
        'urgent_tasks': Task.objects.filter(
            project__in=projects,
            priority__in=['4', '5'],
            status__in=['NEW', 'IN_PROGRESS']
        ).count()
    }

    return stats
