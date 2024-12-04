from django.contrib.auth.hashers import make_password
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission

class UserProfile(AbstractUser):
    email = models.EmailField(max_length=320, verbose_name = "Электронная почта")
    nickname = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Никнейм'
    )

    def save(self, *args, **kwargs):
        # Автоматически заполняем никнейм, если он не указан
        if not self.nickname:
            self.nickname = self.username
        super().save(*args, **kwargs)

    groups = models.ManyToManyField(
        Group,
        related_name='todolist_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='todolist_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def set_password(self, raw_password):
        self.password = make_password(raw_password)



    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = ('Пользователь')
        verbose_name_plural = ('Пользователи')


class UserBIO(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Администратор'),
        ('USER', 'Пользователь'),
        ('MANAGER', 'Менеджер'),
        ('DEVELOPER', 'Разработчик'),
        ('CEO', 'CEO'),
    ]

    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='bio')
    full_name = models.CharField('ФИО', max_length=255)
    company = models.CharField('Компания', max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER', verbose_name = "Роль")
    age = models.IntegerField('Возраст')


    def __str__(self):
        return f"О пользователе {self.user.nickname}"

    class Meta:
        verbose_name = ('О пользователе')
        verbose_name_plural = ('О пользователях')



class Project(models.Model):
    STATUS_CHOICES = [
        ('NEW', ('Новый')),
        ('IN_PROGRESS', ('Выполняется')),
        ('DONE', ('Завершенный')),
    ]

    name = models.CharField(('Название'), max_length=100)
    description = models.TextField(('Описание'))
    status = models.CharField(('Статус'), max_length=20, choices=STATUS_CHOICES, default='NEW')
    created_at = models.DateTimeField(('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(('Дата обновления'), auto_now=True)
    members = models.ManyToManyField(UserProfile, through='UserProfileProject', verbose_name=('Участники'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = ('Проект')
        verbose_name_plural = ('Проекты')


class UserProfileProject(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name=('Пользователь'))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=('Проект'))

    class Meta:
        unique_together = ('user_profile', 'project')
        verbose_name = ('Проект пользователя')
        verbose_name_plural = ('Проекты пользователей')


class Task(models.Model):
    STATUS_CHOICES = [
        ('NEW', ('Новая')),
        ('BACKLOG', ('Бэклог')),
        ('IN_PROGRESS', ('Выполняется')),
        ('DONE', ('Завершена')),
    ]

    PRIORITY_CHOICES = [
        ('1', ('1 приоритет')),
        ('2', ('2 приоритет')),
        ('3', ('3 приоритет')),
        ('4', ('4 приоритет')),
        ('5', ('5 приоритет')),
    ]

    name = models.CharField(('Название'), max_length=100)
    description = models.TextField(('Описание'))
    status = models.CharField(('Статус'), max_length=20, choices=STATUS_CHOICES, default='NEW')
    priority = models.CharField(('Приоритет'), max_length=1, choices=PRIORITY_CHOICES, default='1')
    due_date = models.DateTimeField(('Крайний срок'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=('Дата обновления'))
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name=('Проект'))
    assignee = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name=('Исполнитель'))
    category = models.CharField(('Категория'), max_length=100)

    def clean(self):
        # Валидация даты
        if self.due_date and self.due_date < timezone.now():
            raise ValidationError({
                'due_date': 'Крайний срок не может быть в прошлом.'
            })

        # Валидация уникальности названия задачи для пользователя
        if self.assignee:
            # Исключаем текущий экземпляр при обновлении
            existing_tasks = Task.objects.filter(
                name=self.name,
                assignee=self.assignee
            ).exclude(pk=self.pk)

            if existing_tasks.exists():
                raise ValidationError({
                    'name': 'Задача с таким названием уже существует у этого пользователя.'
                })

    def save(self, *args, **kwargs):
        # Вызов метода clean перед сохранением
        self.full_clean()
        return super().save(*args, **kwargs)

    def validate_subtasks_count(self):
        # Проверка количества подзадач
        subtask_count = self.subtask_set.count()
        if subtask_count > 5:
            raise ValidationError({
                'subtasks': 'Максимальное количество подзадач - 5'
            })

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = ('Задача')
        verbose_name_plural = ('Задачи')


class Subtask(models.Model):
    STATUS_CHOICES = [
        ('NEW', ('Новая')),
        ('IN_PROGRESS', ('Выполняется')),
        ('DONE', ('Завершена')),
    ]

    name = models.CharField(('Название'), max_length=100)
    description = models.TextField(('Описание'))
    status = models.CharField(('Статус'), max_length=20, choices=STATUS_CHOICES, default='NEW')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=('Задача'))

    def clean(self):
        # Проверка количества подзадач перед сохранением
        task = self.task
        subtask_count = task.subtask_set.count()

        # Если это новая подзадача и количество уже 5
        if not self.pk and subtask_count >= 5:
            raise ValidationError({
                'task': 'Невозможно добавить подзадачу. Достигнут максимум (5 подзадач).'
            })

    def save(self, *args, **kwargs):
        # Вызов метода clean перед сохранением
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = ('Подзадача')
        verbose_name_plural = ('Подзадачи')


class Comment(models.Model):
    text = models.TextField(('Текст комментария'))
    created_at = models.DateTimeField(('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(('Дата обновления'), auto_now=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name=('Автор'))
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name=('Задача'))

    def __str__(self):
        return f"Прокомментировано {self.author.nickname} на {self.task.name}"

    class Meta:
        verbose_name = ('Комментарий')
        verbose_name_plural = ('Комментарии')



