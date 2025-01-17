""" Models """
import os
from io import BytesIO
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from simple_history.models import HistoricalRecords
from xhtml2pdf import pisa
from xhtml2pdf.default import DEFAULT_FONT

from django.conf import settings

# class UserProfileManager(models.Manager):
#     """Кастомный менеджер для UserProfile"""
#
#     def active_users(self):
#         return self.filter(is_active=True)
#
#     def get_by_natural_key(self, email):
#         return self.get(email=email)

class UserProfile(AbstractUser):
    """Модель UserProfile"""

    # Существующие поля
    email = models.EmailField(
        max_length=320,
        verbose_name="Электронная почта",
    )

    date_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    def save(self, *args, **kwargs):
        """Хэш паролей"""
        if self._state.adding and not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-date_joined']

    history = HistoricalRecords()

    # Если нужны дополнительные методы
    def get_tasks(self):
        """Получить все задачи пользователя"""
        return self.task_set.all()

    def get_projects(self):
        """Получить все проекты пользователя"""
        return self.project_set.all()


class UserBIO(models.Model):
    """Модель UserBIO"""

    ROLE_CHOICES = [
        ("ADMIN", "Администратор"),
        ("USER", "Пользователь"),
        ("MANAGER", "Менеджер"),
        ("DEVELOPER", "Разработчик"),
        ("CEO", "CEO"),
    ]

    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name="bio"
    )
    company = models.CharField("Компания", max_length=255)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="USER", verbose_name="Роль"
    )
    age = models.IntegerField("Возраст")

    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name="Аватар",
        blank=True,
        null=True
    )

    def __str__(self):
        """Возвращает корректное отображение названия в админке"""
        return f"О пользователе {self.user.username}"  # pylint: disable=no-member

    class Meta:
        # pylint: disable=too-few-public-methods
        """Meta"""
        verbose_name = "О пользователе"
        verbose_name_plural = "О пользователях"

    history = HistoricalRecords()


class Project(models.Model):
    """Модель Project"""

    STATUS_CHOICES = [
        ("NEW", "Новый"),
        ("IN_PROGRESS", "Выполняется"),
        ("DONE", "Завершенный"),
    ]

    name = models.CharField("Название", max_length=100)
    description = models.TextField("Описание")
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="NEW"
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    members = models.ManyToManyField(
        UserProfile, through="UserProfileProject", verbose_name="Участники"
    )

    def __str__(self):
        """Функция возвращает имя проекта"""
        return str(self.name)

    class Meta:
        # pylint: disable=too-few-public-methods
        """Meta"""
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def get_absolute_url(self):
        """Функция возвращает абсолютный URL проекта"""
        return reverse("project_detail", args=[str(self.id)])

    history = HistoricalRecords()


    def get_pdf_report(self):
        """Generates PDF report for the project"""
        if not self.tasks.exists():
            raise ValidationError("No tasks for report.")

        # Словари для перевода
        PROJECT_STATUS_TRANSLATION = {
            "NEW": "New",
            "IN_PROGRESS": "In Progress",
            "DONE": "Done"
        }

        TASK_STATUS_TRANSLATION = {
            "NEW": "New",
            "BACKLOG": "Backlog",
            "IN_PROGRESS": "In Progress",
            "DONE": "Done"
        }

        PRIORITY_TRANSLATION = {
            "1": "Priority 1",
            "2": "Priority 2",
            "3": "Priority 3",
            "4": "Priority 4",
            "5": "Priority 5"
        }

        # Настройка шрифта
        font_path = os.path.join(settings.STATIC_ROOT, 'fonts', 'arial unicode ms.otf')
        if os.path.exists(font_path):
            print(f"Font file exists at: {font_path}")
        else:
            print(f"Font file not found at: {font_path}")
        pdfmetrics.registerFont(TTFont('arial unicode ms', font_path))
        pisa.DEFAULT_FONT = 'arial unicode ms'

        # Подготовка данных проекта
        project_data = {
            'name': self.name,
            'status': PROJECT_STATUS_TRANSLATION.get(self.status, self.status),
            'created_at': self.created_at,
            'description': self.description
        }

        # Подготовка данных задач с переводом
        tasks_translated = []
        for task in self.tasks.all():
            tasks_translated.append({
                'name': task.name,
                'status': TASK_STATUS_TRANSLATION.get(task.status, task.status),
                'priority': PRIORITY_TRANSLATION.get(task.priority, task.priority),
                'due_date': task.due_date
            })

        # Template preparation
        template = get_template('project_report.html')
        context = {
            'project': project_data,  # теперь передаем как project
            'tasks': tasks_translated,
            'members': self.members.all()
        }

        html = template.render(context)

        # PDF generation
        pdf_content = BytesIO()
        status = pisa.CreatePDF(
            BytesIO(html.encode('utf-8')),
            dest=pdf_content,
            encoding='utf-8',
            link_callback=lambda uri, rel: os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
        )
        print(f"Text encoding check: {self.name.encode('utf-8')}")

        if status.err:
            return None

        return pdf_content.getvalue()


history = HistoricalRecords()


class UserProfileProject(models.Model):
    """Модель UserProfileProject"""

    user_profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, verbose_name="Проект"
    )
    role = models.CharField(max_length=50, blank=True, null=True, verbose_name="Роль")
    added_on = models.DateField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        # pylint: disable=too-few-public-methods
        """Meta"""
        unique_together = ("user_profile", "project")
        verbose_name = "Проект пользователя"
        verbose_name_plural = "Проекты пользователей"

    history = HistoricalRecords()


class TaskManager(models.Manager):
    """Модельный менеджер Класс TaskManager"""

    # pylint: disable=too-few-public-methods
    def get_overdue(self):
        """Возвращает список задач, которые должны быть выполнены срочно"""
        return self.filter(
            due_date__lt=timezone.now().date(),
            status__in=["NEW", "BACKLOG", "IN_PROGRESS"],
        )

    def total_tasks(self):
        """Возвращает общее количество задач."""
        return self.aggregate(total=Count('id'))['total']

class Task(models.Model):
    """Модель Task"""

    STATUS_CHOICES = [
        ("NEW", "Новая"),
        ("BACKLOG", "Бэклог"),
        ("IN_PROGRESS", "Выполняется"),
        ("DONE", "Завершена"),
    ]

    PRIORITY_CHOICES = [
        ("1", "1 приоритет"),
        ("2", "2 приоритет"),
        ("3", "3 приоритет"),
        ("4", "4 приоритет"),
        ("5", "5 приоритет"),
    ]

    name = models.CharField("Название", max_length=100)
    description = models.TextField("Описание")
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="NEW"
    )
    priority = models.CharField(
        "Приоритет", max_length=1, choices=PRIORITY_CHOICES, default="1"
    )
    due_date = models.DateField("Крайний срок")
    created_at = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateField(auto_now=True, verbose_name="Дата обновления")
    attachment = models.FileField(
        "Прикрепленный файл",
        upload_to='task_attachments/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Прикрепите файлы к задаче (документы, изображения и т.д.)"
    )

    reference_link = models.URLField(
        "Ссылка на ресурс",
        max_length=200,
        blank=True,
        null=True,
        help_text="Укажите ссылку на внешний ресурс (например, GitHub, Confluence)"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, verbose_name="Проект", related_name='tasks')
    assignee = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Исполнитель",
        related_name="assigned_tasks"
    )
    category = models.CharField("Категория", max_length=100)

    def get_history_changes(self):
        """Метод для получения изменений в читаемом виде"""
        changes = []
        records = self.history.all()
        for i in range(len(records) - 1):
            new_record = records[i]
            old_record = records[i + 1]
            delta = new_record.diff_against(old_record)

            changes_list = []
            for change in delta.changes:
                if change.field == 'updated_at':
                    continue
                field_name = self._meta.get_field(change.field).verbose_name
                changes_list.append(f"{field_name}: с '{change.old}' на '{change.new}'")

            if changes_list:
                changes.append({
                    'date': new_record.history_date,
                    'changes': ', '.join(changes_list)
                })
        return changes

    history = HistoricalRecords()

    objects = TaskManager()

    def clean(self):
        super().clean()  # Сначала вызываем родительский clean()

        # Проверка даты только для новых задач или при изменении даты
        if self.due_date and not self.pk:  # Для новых задач
            if self.due_date < timezone.now().date():
                raise ValidationError({'due_date': 'Дата не может быть в прошлом'})
        elif self.pk:  # Для существующих задач
            original_task = Task.objects.get(pk=self.pk)
            # Проверяем дату только если она была изменена
            if self.due_date != original_task.due_date and self.due_date < timezone.now().date():
                raise ValidationError({'due_date': 'Дата не может быть в прошлом'})

        # Проверка уникальности имени
        if self.name:
            exists_query = Task.objects.filter(
                name=self.name,
                project=self.project  # Добавляем проверку в рамках проекта
            )
            if self.pk:
                exists_query = exists_query.exclude(pk=self.pk)
            if exists_query.exists():
                raise ValidationError({
                    'name': 'Задача с таким названием уже существует в данном проекте'
                })

    def validate_subtasks_count(self):
        """Проверка количества подзадач перед сохранением"""
        subtask_count = self.subtask_set.count()
        if subtask_count > 5:
            raise ValidationError({"subtasks": "Максимальное количество подзадач - 5"})

    def __str__(self):
        """Функция возвращает имя задачи"""
        return str(self.name)

    class Meta:
        # pylint: disable=too-few-public-methods
        """ Meta """
        verbose_name = "задачу"
        verbose_name_plural = "Задачи"
        ordering = ("due_date",)


class Subtask(models.Model):
    """Модель Subtask"""

    STATUS_CHOICES = [
        ("NEW", "Новая"),
        ("IN_PROGRESS", "Выполняется"),
        ("DONE", "Завершена"),
    ]

    name = models.CharField("Название", max_length=100)
    description = models.TextField("Описание")
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="NEW"
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="Задача")

    def clean(self):
        """Проверка количества подзадач перед сохранением"""
        task = self.task
        subtask_count = task.subtask_set.count()

        # Если это новая подзадача и количество уже 5
        if not self.pk and subtask_count >= 5:
            raise ValidationError(
                {
                    "task": "Невозможно добавить подзадачу. \
                    Достигнут максимум (5 подзадач)."
                }
            )

    def save(self, *args, **kwargs):
        """Переопределение метода save для проверки количества подзадач"""
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """Функция возвращает имя подзадачи"""
        return str(self.name)

    class Meta:
        # pylint: disable=too-few-public-methods
        """Meta"""
        verbose_name = "Подзадача"
        verbose_name_plural = "Подзадачи"

    history = HistoricalRecords()


class Comment(models.Model):
    """Модель Comment"""

    text = models.TextField("Текст комментария")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    author = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, verbose_name="Автор"
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="Задача", related_name="comments")  # pylint: disable=invalid-name)

    def __str__(self):
        """Функция возвращает текст комментария"""
        return f"Прокомментировано {self.author.username} на {self.task.name}"

    class Meta:
        # pylint: disable=too-few-public-methods
        """Meta"""
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    history = HistoricalRecords()
