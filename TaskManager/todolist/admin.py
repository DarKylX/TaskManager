from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import UserProfile, UserBIO, Project, UserProfileProject, Task, Subtask, Comment
from import_export.admin import ImportExportModelAdmin
from .resources import TaskResource
from import_export.formats.base_formats import XLSX



class HighPriorityFilter(admin.SimpleListFilter):
    title = 'Расширенный фильтр задач'
    parameter_name = 'task_filter'

    def lookups(self, request, model_admin):
        return (
            ('high_priority_incomplete', 'Высокоприоритетные незавершенные'),
            ('due_tomorrow', 'Дедлайн завтра'),
            ('not_my_tasks', 'Задачи других пользователей'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'high_priority_incomplete':
            return queryset.filter(
                priority='5',
                status__in=['NEW', 'BACKLOG', 'IN_PROGRESS']
            )

        if self.value() == 'due_tomorrow':
            tomorrow = timezone.now() + timedelta(days=1)
            return queryset.filter(due_date__gte=tomorrow, due_date__lt=tomorrow + timedelta(days=1))

        if self.value() == 'not_my_tasks':
            return queryset.exclude(assignee=request.user)

        return queryset

class SubtaskInline(admin.TabularInline):
    model = Subtask
    extra = 4
    fields = ('name', 'description', 'status')


class TaskInline(admin.TabularInline):
    model = Task
    extra = 3
    fields = ('name', 'description', 'status', 'priority', 'due_date', 'assignee')


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('name', 'description', 'status', 'priority', 'due_date', 'assignee', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('status', 'priority', HighPriorityFilter, 'due_date', 'assignee')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'due_date'
    inlines = [SubtaskInline]
    raw_id_fields = ('assignee',)
    resource_class = TaskResource

    # Действия
    actions = [
        'get_high_priority_incomplete_tasks',
        'get_high_priority_or_due_tomorrow',
        'get_tasks_not_belongs_to_user',
        "export_high_priority_tasks"
    ]


    def export_high_priority_tasks(self, request, queryset):
        resource = self.resource_class()
        high_priority_queryset = resource.get_export_queryset()
        dataset = resource.export(high_priority_queryset)
        file_format = XLSX()
        response = file_format.export_data(dataset)
        response_content_type = file_format.get_content_type()
        filename = 'high_priority_tasks.xlsx'
        response = HttpResponse(response, content_type=response_content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    export_high_priority_tasks.short_description = "Экспорт задач с высоким приоритетом"
    def get_high_priority_incomplete_tasks(self, request, queryset):
        """Получение задач, которые не выполнены и имеют высокий приоритет."""
        tasks = queryset.filter(
            status__in=['NEW', 'BACKLOG', 'IN_PROGRESS'],
            priority='5'
        )
        self.message_user(request, f"Найдено высокоприоритетных незавершенных задач: {tasks.count()}")

    get_high_priority_incomplete_tasks.short_description = "Высокоприоритетные незавершенные задачи"

    def get_high_priority_or_due_tomorrow(self, request, queryset):
        """Найти все задачи, которые либо имеют высокий приоритет и не завершены, либо задачи, которые должны быть выполнены завтра."""
        tomorrow = timezone.now() + timedelta(days=1)
        tasks = queryset.filter(
            Q(priority='5', status__in=['NEW', 'BACKLOG', 'IN_PROGRESS']) |
            Q(due_date=tomorrow.date())
        )
        self.message_user(request, f"Найдено задач высокого приоритета или с дедлайном завтра: {tasks.count()}")

    get_high_priority_or_due_tomorrow.short_description = "Задачи высокого приоритета или с дедлайном завтра"

    def get_tasks_not_belongs_to_user(self, request, queryset):
        """Найти все задачи, которые не принадлежат текущему пользователю."""
        tasks = queryset.exclude(assignee=request.user).filter(
            status__in=['IN_PROGRESS', 'BACKLOG']
        )
        self.message_user(request, f"Найдено задач, не принадлежащих текущему пользователю: {tasks.count()}")

    get_tasks_not_belongs_to_user.short_description = "Задачи других пользователей"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


@admin.register(UserBIO)
class UserBIOAdmin(admin.ModelAdmin):
    list_display = ('role', 'formatted_age', 'user')
    search_fields = ('user__username',)
    list_display_links = ('user',)


    @admin.display(ordering='age', description="Возраст в годах")
    def formatted_age(self, obj):
        return obj.age if obj.age>18 else "Проверить возраст"

class UserProfileProjectInline(admin.TabularInline):
    model = UserProfileProject
    extra = 1
    verbose_name = "Связь пользователя и проекта"
    verbose_name_plural = "Связи пользователей и проектов"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('name', 'description')
    inlines = [TaskInline, UserProfileProjectInline]



@admin.register(UserProfileProject)
class UserProfileProjectAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'project', 'role', 'added_on')
    search_fields = ('user_profile__username', 'project__name')


@admin.register(Subtask)
class SubtaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'task')
    list_filter = ('status', 'task')
    search_fields = ('name',)




@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'task', 'created_at')
    search_fields = ('text', 'task__name', 'author__username')
