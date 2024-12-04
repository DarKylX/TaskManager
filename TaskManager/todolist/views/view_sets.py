from datetime import timezone, timedelta
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import UserProfile, UserBIO, Project, UserProfileProject, Task, Subtask, Comment
from ..serializers.todolists import (
    UserProfileSerializer,
    UserBiosSerializer,
    ProjectSerializer,
    UserProfileProjectSerializer,
    TaskSerializer,
    SubtaskSerializer,
    CommentSerializer,
    SubtaskCreateSerializer
)


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @swagger_auto_schema(
        operation_summary="Получение всех профилей пользователей",
        responses={200: UserProfileSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание нового профиля пользователя",
        request_body=UserProfileSerializer,
        responses={201: UserProfileSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class UserBIOViewSet(viewsets.ModelViewSet):
    queryset = UserBIO.objects.all()
    serializer_class = UserBiosSerializer

    @swagger_auto_schema(
        operation_summary="Получение всех биографий пользователей",
        responses={200: UserBiosSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @swagger_auto_schema(
        operation_summary="Получение всех проектов",
        responses={200: ProjectSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание нового проекта",
        request_body=ProjectSerializer,
        responses={201: ProjectSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class UserProfileProjectViewSet(viewsets.ModelViewSet):
    queryset = UserProfileProject.objects.all()
    serializer_class = UserProfileProjectSerializer

    @swagger_auto_schema(
        operation_summary="Получение всех связей между пользователями и проектами",
        responses={200: UserProfileProjectSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @swagger_auto_schema(
        operation_summary="Получение всех задач",
        responses={200: TaskSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание новой задачи",
        request_body=TaskSerializer,
        responses={201: TaskSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получение задач, которые должны быть выполнены в ближайшие 7 дней",
    )
    @action(detail=False, methods=['GET'])
    def due_soon(self, request):
        """Получение задач, которые должны быть выполнены в ближайшие 7 дней."""
        seven_days_from_now = timezone.now() + timedelta(days=7)
        tasks = Task.objects.filter(due_date__lte=seven_days_from_now, status='NEW')
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Поиск задач по описанию",
        responses={200: TaskSerializer(many=True)},
        parameters=[
            openapi.Parameter('search_term', openapi.IN_QUERY, description="Термин для поиска в описании задачи",
                              type=openapi.TYPE_STRING)
        ]
    )
    @action(detail=False, methods=['GET'])
    def search_description(self, request):
        """Поиск задач, содержащих определенное слово в описании."""
        search_term = request.query_params.get('search_term', None)
        if not search_term:
            return Response({"detail": "Search term is required."}, status=status.HTTP_400_BAD_REQUEST)

        tasks = Task.objects.filter(description__icontains=search_term)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Получение задач с высоким приоритетом и статусом 'новая' или 'в процессе'",
        responses={200: TaskSerializer(many=True)}
    )
    @action(detail=False, methods=['GET'])
    def high_priority_incomplete(self, request):
        """Получение задач, которые не выполнены и имеют высокий приоритет."""
        tasks = Task.objects.filter(status__in=['NEW', 'BACKLOG', 'IN_PROGRESS'],
                                    priority='5')  # Assuming '5' is high priority
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Получение задач с высоким приоритетом или с датой выполнения завтра",
        responses={200: TaskSerializer(many=True)}
    )
    @action(detail=False, methods=['GET'])
    def high_priority_or_due_tomorrow(self, request):
        """Найти все задачи, которые либо имеют высокий приоритет и не завершены, либо задачи, которые должны быть выполнены завтра."""
        tomorrow = timezone.now() + timedelta(days=1)
        tasks = Task.objects.filter(
            (Q(priority='5', status__in=['NEW', 'BACKLOG', 'IN_PROGRESS'])) |
            (Q(due_date__date=tomorrow.date()))
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Получение задач, которые не принадлежат текущему пользователю",
        responses={200: TaskSerializer(many=True)}
    )
    @action(detail=False, methods=['GET'])
    def not_belongs_to_user(self, request):
        """Найти все задачи, которые не принадлежат текущему пользователю, но имеют статус "в процессе" или "отменены"."""
        user = request.user
        tasks = Task.objects.exclude(assignee=user).filter(status__in=['IN_PROGRESS', 'BACKLOG'])  # Adjusted status
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class SubtaskViewSet(viewsets.ModelViewSet):
    queryset = Subtask.objects.all()

    @swagger_auto_schema(
        operation_summary="Получение всех подзадач",
        responses={200: SubtaskSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание новой подзадачи",
        request_body=SubtaskCreateSerializer,
        responses={201: SubtaskCreateSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновление подзадачи",
        request_body=SubtaskCreateSerializer,
        responses={200: SubtaskCreateSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    @swagger_auto_schema(
        operation_summary="Получение всех комментариев",
        responses={200: CommentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание нового комментария",
        request_body=CommentSerializer,
        responses={201: CommentSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
