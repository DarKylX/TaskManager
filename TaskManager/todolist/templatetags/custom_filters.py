from django import template
from datetime import datetime

register = template.Library()

@register.filter(name='days_until')
def days_until(value):
    """Возвращает количество дней до указанной даты"""
    if not value:
        return ""
    delta = value - datetime.now().date()

    def get_days_label(days):
        if days % 100 in [11, 12, 13, 14]:
            return 'дней'
        if days % 10 == 1:
            return 'день'
        if days % 10 in [2, 3, 4]:
            return 'дня'
        return 'дней'

    if delta.days < 0:
        return "Просрочено"
    if delta.days == 0:
        return "Сегодня"
    if delta.days == 1:
        return "Завтра"
    else:
        return f"{delta.days} {get_days_label(delta.days)}"

@register.filter(name='priority_badge')
def priority_badge(priority):
    """Возвращает класс badge в зависимости от приоритета"""
    classes = {
        '5': 'badge bg-danger',
        '4': 'badge bg-danger',
        '3': 'badge bg-warning text-dark',
        '2': 'badge bg-warning text-dark',
        '1': 'badge bg-info text-dark'
    }
    return classes.get(priority, 'badge bg-secondary')
