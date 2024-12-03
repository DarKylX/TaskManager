from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class UserProfile(AbstractUser):
    nickname = models.CharField(max_length=100)
    email = models.EmailField(max_length=320)

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

    def __str__(self):
        return self.nickname



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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    age = models.IntegerField('Возраст')

    def __str__(self):
        return f"О пользователе {self.user.nickname}"


class Project(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Новый'),
        ('IN_PROGRESS', 'Выполняется'),
        ('DONE', 'Завершенный'),
   ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(UserProfile, through='UserProfileProject')

    def __str__(self):
        return self.name


class UserProfileProject(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user_profile', 'project')


class Task(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Новая'),
        ('BACKLOG', 'Бэклог'),
        ('IN_PROGRESS', 'Выполняется'),
        ('DONE', 'Завершена'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', '3 приоритет'),
        ('MEDIUM', '2 приоритет'),
        ('HIGH', '1 приориотет'),
        ('NO', '0 приоритет')
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='NO')
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assignee = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Subtask(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'Новая'),
        ('IN_PROGRESS', 'Выполняется'),
        ('DONE', 'Завершена'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return f"Прокомментировано {self.author.nickname} на {self.task.name}"
