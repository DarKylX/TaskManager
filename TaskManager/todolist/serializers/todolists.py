from rest_framework import serializers
from django.utils import timezone
from ..models import UserProfile, UserBIO, Project, UserProfileProject, Task, Subtask, Comment


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserBiosSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBIO
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class UserProfileProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileProject
        fields = '__all__'


class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    subtasks = SubtaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'

    def validate(self, attrs):
        # Получаем текущего пользователя
        user = self.context['request'].user

        # Проверка уникальности названия задачи для пользователя
        # Важно: различаем создание новой задачи и обновление существующей
        task_name = attrs.get('name')

        # Если это создание новой задачи
        if not self.instance:
            # Проверяем существование задачи с таким же именем для этого пользователя
            existing_task = Task.objects.filter(
                name=task_name,
                assignee=user
            ).exists()

            if existing_task:
                raise serializers.ValidationError({
                    "name": "Задача с таким названием уже существует для этого пользователя."
                })

        return attrs

    def create(self, validated_data):
        # Создаем задачу
        task = super().create(validated_data)

        # Проверяем количество подзадач при создании
        self.validate_subtask_count(task)

        return task

    def update(self, instance, validated_data):
        # Обновляем задачу
        updated_task = super().update(instance, validated_data)

        # Проверяем количество подзадач при обновлении
        self.validate_subtask_count(updated_task)

        return updated_task

    def validate_subtask_count(self, task):
        # Получаем количество подзадач для этой задачи
        subtask_count = Subtask.objects.filter(task=task).count()

        # Проверяем, не превышает ли количество подзадач 5
        if subtask_count > 5:
            raise serializers.ValidationError({
                "subtasks": "Максимальное количество подзадач - 5."
            })


# Специальный сериализатор для создания подзадачи с проверкой лимита
class SubtaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = '__all__'

    def validate(self, attrs):
        # Получаем задачу
        task = attrs.get('task')

        # Получаем количество текущих подзадач
        subtask_count = Subtask.objects.filter(task=task).count()

        # Проверяем, не превышает ли количество подзадач 5
        if subtask_count >= 5:
            raise serializers.ValidationError({
                "task": "Невозможно добавить подзадачу. Достигнут максимум (5 подзадач)."
            })

        return attrs
