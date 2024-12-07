from math import asinh

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from ..models import UserProfile, UserBIO, Project, UserProfileProject, Task, Subtask, Comment


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserBiosSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all(), required=True)

    class Meta:
        model = UserBIO
        fields = ['user', 'company', 'role', 'age']

    def create(self, validated_data):
        user = validated_data.get('user')

        # Проверяем, существует ли уже биография для этого пользователя
        user_bio = UserBIO.objects.filter(user=user).first()

        # Если биография существует, обновляем ее, иначе создаем новую
        if user_bio:
            # Обновляем данные существующей биографии
            user_bio.company = validated_data.get('company', user_bio.company)
            user_bio.role = validated_data.get('role', user_bio.role)
            user_bio.age = validated_data.get('age', user_bio.age)
            user_bio.save()
            return user_bio
        else:
            # Если биографии нет, создаем новую
            user_bio = UserBIO.objects.create(**validated_data)
            return user_bio

    def update(self, instance, validated_data):
        instance.company = validated_data.get('company', instance.company)
        instance.role = validated_data.get('role', instance.role)
        instance.age = validated_data.get('age', instance.age)
        instance.save()
        return instance

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

    def validate_due_date(self, value):
        # Проверка, что дата окончания не раньше текущей
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Дата окончания не может быть в прошлом.")
        return value

    def validate_priority(self, value):
        # Проверка, что приоритет в пределах 1-5
        if value not in ['1', '2', '3', '4', '5']:
            raise serializers.ValidationError("Приоритет должен быть от 1 до 5.")
        return value


    def validate(self, attrs):
        task_name = attrs.get('name')
        user = attrs.get('assignee')
        # Если это создание новой задачи
        if not self.instance:
            # Проверяем существование задачи с таким же именем для этого пользователя
            existing_task = Task.objects.filter(
                name=task_name,
                assignee=user
            ).exists()

            if existing_task:
                raise serializers.ValidationError("Задача с таким названием уже существует для этого пользователя.")

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
        task = attrs.get('task')
        subtask_name = attrs.get('name')

        # Если это создание новой подзадачи
        if not self.instance:
            # Проверяем, не существует ли подзадача с таким же названием для этой задачи
            existing_subtask = Subtask.objects.filter(task=task, name=subtask_name).exists()
            if existing_subtask:
                raise serializers.ValidationError({
                    "name": "Подзадача с таким именем уже существует для этой задачи."
                })
        else:
            # Если это обновление, проверяем уникальность имени подзадачи в пределах задачи
            subtask_pk = attrs.get('pk')
            existing_subtask = Subtask.objects.filter(task=task, name=subtask_name).exclude(pk=subtask_pk).exists()
            if existing_subtask:
                raise serializers.ValidationError({
                    "name": "Подзадача с таким именем уже существует для этой задачи."
                })

        # Получаем количество текущих подзадач
        subtask_count = Subtask.objects.filter(task=task).count()

        # Проверяем, не превышает ли количество подзадач 5
        if subtask_count >= 5:
            raise serializers.ValidationError({
                "task": "Невозможно добавить подзадачу. Достигнут максимум (5 подзадач)."
            })

        return attrs
