from import_export import resources
from .models import Task

class TaskResource(resources.ModelResource):
    class Meta:
        model = Task
        fields = ('name', 'description', 'status', 'priority', 'due_date')

    def get_export_queryset(self, request=None):
        """Возвращает набор данных для экспорта, включая только задачи с высоким приоритетом."""
        return Task.objects.filter(priority='5')

    def dehydrate_due_date(self, task):
        """Преобразует поле due_date в формат "DD-MM-YYYY"."""
        return task.due_date.strftime('%d-%m-%Y')

    def get_status(self, task):
        """Преобразует поле status в более читабельный формат."""
        status_map = {
            'NEW': 'New',
            'BACKLOG': 'Backlog',
            'IN_PROGRESS': 'In Progress',
            'DONE': 'Completed',
            'CANCELED': 'Canceled'
        }
        return status_map.get(task.status, task.status)
