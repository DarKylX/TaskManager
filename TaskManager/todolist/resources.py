"""Экспорт """

from import_export import resources
from .models import Task


class TaskResource(resources.ModelResource):
    """Функции для преобразований при экспорте"""

    class Meta:
        """Meta information"""

        # pylint: disable=too-few-public-methods
        model = Task
        fields = ("name", "description", "status", "priority", "due_date")

    def get_export_queryset(self, _request=None):
        """Возвращает набор данных для экспорта, \
        включая только задачи с высоким приоритетом."""
        return Task.objects.filter(priority="5")

    def dehydrate_due_date(self, task):
        """Преобразует поле due_date в формат "DD-MM-YYYY"."""
        return task.due_date.strftime("%d-%m-%Y")

    def dehydrate_status(self, task):
        """Преобразует поле status в более читабельный формат."""
        status_map = {
            "NEW": "Новая",
            "BACKLOG": "Архив",
            "IN_PROGRESS": "В процессе",
            "DONE": "Выполнена",
            "CANCELED": "Отменена",
        }
        return status_map.get(task.status, task.status)
