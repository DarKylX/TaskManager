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

    @swagger_auto_schema(
        operation_summary="Обновление профиля пользователя",
        request_body=UserProfileSerializer,
        responses={200: UserProfileSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление профиля пользователя",
        request_body=UserProfileSerializer,
        responses={200: UserProfileSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление профиля пользователя",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UserBIOViewSet(viewsets.ModelViewSet):
    queryset = UserBIO.objects.all()
    serializer_class = UserBiosSerializer

    @swagger_auto_schema(
        operation_summary="Получение всех биографий пользователей",
        responses={200: UserBiosSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание новой биографии пользователя",
        request_body=UserBiosSerializer,
        responses={201: UserBiosSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновление биографии пользователя",
        request_body=UserBiosSerializer,
        responses={200: UserBiosSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление биографии пользователя",
        request_body=UserBiosSerializer,
        responses={200: UserBiosSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление биографии пользователя",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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

    @swagger_auto_schema(
        operation_summary="Обновление проекта",
        request_body=ProjectSerializer,
        responses={200: ProjectSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление проекта",
        request_body=ProjectSerializer,
        responses={200: ProjectSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление проекта",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UserProfileProjectViewSet(viewsets.ModelViewSet):
    queryset = UserProfileProject.objects.all()
    serializer_class = UserProfileProjectSerializer

    @swagger_auto_schema(
        operation_summary="Получение всех связей между пользователями и проектами",
        responses={200: UserProfileProjectSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание новой связи между пользователем и проектом",
        request_body=UserProfileProjectSerializer,
        responses={201: UserProfileProjectSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновление связи между пользователем и проектом",
        request_body=UserProfileProjectSerializer,
        responses={200: UserProfileProjectSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление связи между пользователем и проектом",
        request_body=UserProfileProjectSerializer,
        responses={200: UserProfileProjectSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление связи между пользователем и проектом",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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
        operation_summary="Обновление задачи",
        request_body=TaskSerializer,
        responses={200: TaskSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление задачи",
        request_body=TaskSerializer,
        responses={200: TaskSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление задачи",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    # Custom actions
    @swagger_auto_schema(
        operation_summary="Получение задач, которые должны быть выполнены в ближайшие 7 дней",
    )
    @action(detail=False, methods=['GET'])
    def due_soon(self, request):
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
    def search(self, request):
        search_term = request.query_params.get('search_term', '')
        tasks = Task.objects.filter(description__icontains=search_term)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)


class SubtaskViewSet(viewsets.ModelViewSet):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer

    @swagger_auto_schema(
        operation_summary="Получение всех подзадач",
        responses={200: SubtaskSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание новой подзадачи",
        request_body=SubtaskSerializer,
        responses={201: SubtaskSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновление подзадачи",
        request_body=SubtaskSerializer,
        responses={200: SubtaskSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление подзадачи",
        request_body=SubtaskSerializer,
        responses={200: SubtaskSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление подзадачи",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


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

    @swagger_auto_schema(
        operation_summary="Обновление комментария",
        request_body=CommentSerializer,
        responses={200: CommentSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление комментария",
        request_body=CommentSerializer,
        responses={200: CommentSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление комментария",
        responses={204: 'No Content'}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
