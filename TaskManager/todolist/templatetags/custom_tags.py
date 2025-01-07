from django import template
from ..models import Task

register = template.Library()

@register.simple_tag
def task_count():
    """Возвращает количество задач - простой шаблонный тег"""
    return Task.objects.count()

@register.simple_tag
def all_tasks():
    """Возвращает список всех задач -
    Создание шаблонного тега, возвращающего набор запросов """
    tasks = Task.objects.all()
    return tasks

@register.simple_tag
def task_count_not_done():
    """Возвращает количество несделанных задач - простой шаблонный тег"""
    return Task.objects.exclude(status="DONE").count()

# @register.simple_tag(takes_context=True)
# def user_task_count(context):
#     """Возвращает количество несделанных задач текущего пользователя -
#     создание шаблонного тега с контекстными переменными"""
#     user = context['user']
#     return user.task_set.exclude(status="DONE").count()

@register.filter
def uppercase(value):
    """Переводит текст в верхний регистр - шаблонный фильтр"""
    return value.upper()

@register.filter
def truncate(value, length):
    """Обрезает строку до указанной длины - шаблонный фильтр"""
    if len(value) > length:
        return value[:length] + "..."
    return value

@register.simple_tag(takes_context=True)
def tasks_by_status(context, status):
    """
    Возвращает задачи с указанным статусом.
    :param context: контекст шаблона
    :param status: статус задач для фильтрации
    :return: QuerySet задач
    """
    print(f"Статус: {status}, Контекст: {context}")

    return Task.objects.filter(status=status)
