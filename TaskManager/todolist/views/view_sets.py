from datetime import timedelta
import django_filters
from django.utils import timezone
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from simple_history.utils import update_change_reason

from ..filters import TaskFilter, UserBIOFilter

from ..models import UserProfile, UserBIO, Project, UserProfileProject, Task, Subtask, Comment
from ..serializers.todolists import (
    UserProfileSerializer,
    UserBiosSerializer,
    ProjectSerializer,
    UserProfileProjectSerializer,
    TaskSerializer,
    SubtaskSerializer,
    CommentSerializer, SubtaskCreateSerializer, HistoricalTaskSerializer,

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
    filter_backends = [DjangoFilterBackend,]
    filterset_class = UserBIOFilter

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
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description']

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

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class TaskViewSet(viewsets.ModelViewSet):

    queryset = Task.objects.all().order_by('id')
    serializer_class = TaskSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)  # Указываем, что фильтры будут использоваться
    filterset_class = TaskFilter  # Подключаем фильтр
    pagination_class = StandardResultsSetPagination

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
        instance = self.get_object()

        # Проверка измененных данных
        changes = []
        for field, value in request.data.items():
            if hasattr(instance, field) and getattr(instance, field) != value:
                changes.append(f"{field}: {getattr(instance, field)} -> {value}")

        # Записываем причину изменения
        reason = "; ".join(changes) if changes else "Изменение данных"
        update_change_reason(instance, reason)
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

    @swagger_auto_schema(
        operation_summary="Получение истории задачи",
        responses={200: TaskSerializer(many=True)}
    )
    @action(methods=['get'], detail=True)
    def history(self, request, pk=None):
        task = self.get_object()
        history = task.history.all()  # Получаем историю задачи
        serializer = HistoricalTaskSerializer(history, many=True)  # Сериализуем историю
        return Response(serializer.data)


    @swagger_auto_schema(
        operation_summary="Изменение статуса задачи",
        request_body=TaskSerializer,
        responses={200: openapi.Response('Success', TaskSerializer)}

    )
    @action(methods=['post'], detail=True)
    def change_status(self, request, pk=None, **kwargs):
        task = self.get_object()
        new_status = kwargs.get('status')
        if not new_status:
            return Response({"detail": "Необходим новый статус для задачи."}, status=status.HTTP_400_BAD_REQUEST)
        valid_statuses = ['backlog', 'in_progress', 'done', 'new']
        normalized_status = new_status.lower()
        if normalized_status not in valid_statuses:
            return Response({"detail": "Неверный статус."}, status=status.HTTP_400_BAD_REQUEST)
        task.status = normalized_status.upper()
        task.save()

        return Response({"detail": "Статус обновлен."}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Получение просроченных задач"
    )
    @action(detail=False, methods=['GET'])
    def overdue_tasks(self, request):
        today = timezone.now().date()
        overdue_tasks = Task.objects.filter(due_date__lt=today, status__in=['NEW', 'BACKLOG', 'IN_PROGRESS'])
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Поиск задач по описанию",
        responses={200: TaskSerializer(many=True)},
        parameters=[
            openapi.Parameter('search_term', openapi.IN_QUERY, description="Термин для поиска в описании задачи",
                              type=openapi.TYPE_STRING)
        ]
    )
    @action(detail=False, methods=['GET'], url_path='search')
    def get_search(self, request):
        queryset = self.get_queryset()
        # Получение задач, которые должны быть выполнены в ближайшие 7 дней
        if 'due_soon' in self.request.query_params:
            today = timezone.now().date()
            seven_days_later = today + timedelta(days=7)
            queryset = queryset.filter(due_date__gte=today, due_date__lte=seven_days_later)

        # Фильтрация задач с высоким приоритетом или с датой выполнения завтра
        if 'priority_or_due_tomorrow' in self.request.query_params:
            tomorrow = timezone.now().date() + timedelta(days=1)
            queryset = queryset.filter(
                Q(priority='5') | Q(due_date=tomorrow)
            )

        # Фильтрация задач, которые не выполнены и имеют высокий приоритет
        if 'high_priority' in self.request.query_params:
            queryset = queryset.filter(
                ~Q(status='DONE') & Q(priority='5')
            )

        # Задачи, которые не принадлежат текущему пользователю и имеют статус "в процессе" или "отменены"
        if 'not_assigned_to_user' in self.request.query_params:
            user = self.request.user
            queryset = queryset.filter(
                ~Q(assignee=user) & Q(status__in=['IN_PROGRESS', 'CANCELED'])
            )

        # Фильтрация по параметру 'search' (по title или description)
        if 'search_term' in self.request.query_params:
            search_term = self.request.query_params.get('search_term', '')
            queryset = queryset.filter(Q(name__icontains=search_term) | Q(description__icontains=search_term))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class SubtaskViewSet(viewsets.ModelViewSet):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer

    def get_serializer_class(self):

        if self.action in ['create', 'update', 'partial_update']:
            return SubtaskCreateSerializer
        return SubtaskSerializer

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

