""" Вьюсеты """

# pylint: disable=too-many-ancestors
# pylint: disable=logging-fstring-interpolation
import logging
from datetime import timedelta

import django_filters
from django.core.cache import cache
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from simple_history.utils import update_change_reason

from ..filters import TaskFilter, UserBIOFilter
from ..models import (
    Comment,
    Project,
    Subtask,
    Task,
    UserBIO,
    UserProfile,
    UserProfileProject,
)
from ..serializers.RegisterSerializer import RegisterSerializer
from ..serializers.todolists import (
    CommentSerializer,
    HistoricalTaskSerializer,
    ProjectSerializer,
    SubtaskCreateSerializer,
    SubtaskSerializer,
    TaskSerializer,
    UserBiosSerializer,
    UserProfileProjectSerializer,
    UserProfileSerializer,
)

logger = logging.getLogger("todolist")


class UserProfileViewSet(viewsets.ModelViewSet):
    """Вьюсет профилей"""

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        """
        Получение списка профилей с использованием кеширования
        """
        cache_key = "all_user_profiles"
        queryset = cache.get(cache_key)
        if queryset is None:
            queryset = UserProfile.objects.all()
            cache.set(
                cache_key, list(queryset), timeout=60 * 15
            )  # Кэшируем список на 15 минут
        else:
            # Преобразуем кэшированный список обратно в QuerySet
            queryset = UserProfile.objects.filter(
                id__in=[profile.id for profile in queryset]
            )

        return queryset

    @swagger_auto_schema(
        operation_summary="Получение всех профилей пользователей",
        responses={200: UserProfileSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """Отображение пользователей"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание нового профиля пользователя",
        request_body=UserProfileSerializer,
        responses={201: UserProfileSerializer()},
    )
    def create(self, request, *args, **kwargs):
        """Создание нового профиля"""
        response = super().create(request, *args, **kwargs)
        # Инвалидируем кеш после создания
        if response.status_code == status.HTTP_201_CREATED:
            cache.delete("all_user_profiles")
        return response

    @swagger_auto_schema(
        operation_summary="Обновление профиля пользователя",
        request_body=UserProfileSerializer,
        responses={200: UserProfileSerializer()},
    )
    def update(self, request, *args, **kwargs):
        """Обновление информации о пользователе"""
        response = super().update(request, *args, **kwargs)
        # Инвалидируем кеш после обновления
        if response.status_code == status.HTTP_200_OK:
            cache.delete("all_user_profiles")
        return response

    @swagger_auto_schema(
        operation_summary="Частичное обновление профиля пользователя",
        request_body=UserProfileSerializer,
        responses={200: UserProfileSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление информации о пользователе"""
        response = super().partial_update(request, *args, **kwargs)
        # Инвалидируем кеш после частичного обновления
        cache.delete("all_user_profiles")
        cache.delete(f'user_profile_{kwargs.get("pk")}')
        return response

    @swagger_auto_schema(
        operation_summary="Удаление профиля пользователя", responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        """Удаление функции"""
        # Инвалидируем кеш перед удалением
        response = super().destroy(request, *args, **kwargs)
        if response.status_code == status.HTTP_204_NO_CONTENT:
            cache.delete("all_user_profiles")
        return response

    def retrieve(self, request, *args, **kwargs):
        """
        Получение конкретного профиля с использованием кеширования
        """
        pk = kwargs.get("pk")
        cache_key = f"user_profile_{pk}"

        # Пытаемся получить данные из кеша
        instance = cache.get(cache_key)

        if instance is None:
            instance = self.get_object()
            # Кешируем на 15 минут
            cache.set(cache_key, instance, timeout=60 * 15)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserBIOViewSet(viewsets.ModelViewSet):
    """Вьюсет BIO пользователя"""

    queryset = UserBIO.objects.all().order_by("age")
    serializer_class = UserBiosSerializer
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = UserBIOFilter

    @swagger_auto_schema(
        operation_summary="Получение всех биографий пользователей",
        responses={200: UserBiosSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """Отображение биографий пользователей"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание новой биографии пользователя",
        request_body=UserBiosSerializer,
        responses={201: UserBiosSerializer()},
    )
    def create(self, request, *args, **kwargs):
        """Создание новой биографии"""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновление биографии пользователя",
        request_body=UserBiosSerializer,
        responses={200: UserBiosSerializer()},
    )
    def update(self, request, *args, **kwargs):
        """Обновление информации о пользователе"""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление биографии пользователя",
        request_body=UserBiosSerializer,
        responses={200: UserBiosSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление информации о пользователе"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление биографии пользователя",
        responses={204: "No Content"},
    )
    def destroy(self, request, *args, **kwargs):
        """Удаление био"""
        return super().destroy(request, *args, **kwargs)


class ProjectViewSet(viewsets.ModelViewSet):
    """Вьюсет проектов"""

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "description"]

    @swagger_auto_schema(
        operation_summary="Получение всех проектов",
        responses={200: ProjectSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """Отображение проектов"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание нового проекта",
        request_body=ProjectSerializer,
        responses={201: ProjectSerializer()},
    )
    def create(self, request, *args, **kwargs):
        """Создание нового проекта"""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновление проекта",
        request_body=ProjectSerializer,
        responses={200: ProjectSerializer()},
    )
    def update(self, request, *args, **kwargs):
        """Обновление информации о проекте"""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление проекта",
        request_body=ProjectSerializer,
        responses={200: ProjectSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление информации о проекте"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление проекта", responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        """Удаление проекта"""
        return super().destroy(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        project = self.get_object()
        if not project.members.filter(pk=request.user.pk).exists():
            return Response(
                {"error": "У вас нет доступа к этому проекту"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().retrieve(request, *args, **kwargs)


class UserProfileProjectViewSet(viewsets.ModelViewSet):
    """Вьюсет связей между пользователями и проектами"""

    queryset = UserProfileProject.objects.all()
    serializer_class = UserProfileProjectSerializer

    @swagger_auto_schema(
        operation_summary="Получение всех связей между пользователями и проектами",
        responses={200: UserProfileProjectSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """Отображение связей"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание новой связи между пользователем и проектом",
        request_body=UserProfileProjectSerializer,
        responses={201: UserProfileProjectSerializer()},
    )
    def create(self, request, *args, **kwargs):
        """Создание связи"""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновление связи между пользователем и проектом",
        request_body=UserProfileProjectSerializer,
        responses={200: UserProfileProjectSerializer()},
    )
    def update(self, request, *args, **kwargs):
        """Обновление связей"""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление связи между пользователем и проектом",
        request_body=UserProfileProjectSerializer,
        responses={200: UserProfileProjectSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление связей"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление связи между пользователем и проектом",
        responses={204: "No Content"},
    )
    def destroy(self, request, *args, **kwargs):
        """Удаление связи"""
        return super().destroy(request, *args, **kwargs)


class StandardResultsSetPagination(PageNumberPagination):
    """Пагинация результатов"""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class TaskViewSet(viewsets.ModelViewSet):
    """Вьюсет задач"""

    queryset = Task.objects.all().order_by("id")
    serializer_class = TaskSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = TaskFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        cache_key = "all_tasks"
        task_ids = cache.get(cache_key)

        if task_ids:
            logger.debug(f"[CACHE HIT] Получены задачи из кеша: {task_ids}")
            queryset = Task.objects.filter(id__in=task_ids).order_by("id")
        else:
            logger.debug("[CACHE MISS] Кеш пуст. Загружаем из базы данных.")
            queryset = Task.objects.all().order_by("id")
            task_ids = list(queryset.values_list("id", flat=True))
            cache.set(cache_key, task_ids, timeout=60 * 15)
            logger.debug(
                f"[CACHE SET] Ключ '{cache_key}' установлен со значением: {task_ids}"
            )
            logger.debug(f"[CACHE SET] Задачи сохранены в кеш: {task_ids}")
        return queryset

    @action(detail=True, methods=["get"])
    def get_task_details(self, _request, pk=None):
        """Получение детальной информации о задаче"""
        task = get_object_or_404(Task, pk=pk)
        return Response(TaskSerializer(task).data)

    @swagger_auto_schema(
        operation_summary="Получение всех задач",
        responses={200: TaskSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """Отображение всех задач"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание новой задачи",
        request_body=TaskSerializer,
        responses={201: TaskSerializer()},
    )
    def create(self, request, *args, **kwargs):
        """Создание задачи"""
        logger.debug("[DEBUG] Начало создания задачи.")
        logger.debug(f"[DEBUG] Данные запроса: {request.data}")
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            logger.debug("[DEBUG] Задача успешно создана.")
            logger.debug(f"[DEBUG] Данные созданной задачи: {response.data}")
            # Инвалидируем кэш после создания задачи
            cache.delete("all_tasks")
            logger.debug("[DEBUG] Кэш задач сброшен.")
        else:
            logger.debug(
                f"[DEBUG] Ошибка при создании задачи. Статус: {response.status_code}"
            )
            logger.debug(f"[DEBUG] Ответ сервера: {response.data}")
        return response

    @swagger_auto_schema(
        operation_summary="Обновление задачи",
        request_body=TaskSerializer,
        responses={200: TaskSerializer()},
    )
    def update(self, request, *args, **kwargs):
        """Обновление задачи"""
        instance = self.get_object()

        # Проверка измененных данных
        changes = []
        for field, value in request.data.items():
            if hasattr(instance, field) and getattr(instance, field) != value:
                changes.append(f"{field}: {getattr(instance, field)} -> {value}")

        # Записываем причину изменения
        reason = "; ".join(changes) if changes else "Изменение данных"

        # Сохраняем изменения
        response = super().update(request, *args, **kwargs)

        # Обновляем причину изменения после сохранения
        if response.status_code == 200:
            updated_instance = self.get_object()
            update_change_reason(updated_instance, reason)

        return response

    @swagger_auto_schema(
        operation_summary="Частичное обновление задачи",
        request_body=TaskSerializer,
        responses={200: TaskSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление задачи"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление задачи", responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        """Удаление задачи"""
        task = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        # Инвалидируем кеш после удаления
        if task.assignee:
            cache.delete("all_tasks")
            logger.debug("[DEBUG] Кэш задач сброшен.")
        return response

    @swagger_auto_schema(
        operation_summary="Получение истории задачи",
        responses={200: TaskSerializer(many=True)},
    )
    @action(methods=["get"], detail=True)
    def history(self, _request, _pk=None):
        """Получение истории задачи"""
        task = self.get_object()
        history = task.history.all()  # Получаем историю задачи
        serializer = HistoricalTaskSerializer(history, many=True)  # Сериализуем историю
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Изменение статуса задачи",
        request_body=TaskSerializer,
        responses={200: openapi.Response("Success", TaskSerializer)},
    )
    @action(methods=["post"], detail=True)
    def change_status(self, _request, _pk=None, **kwargs):
        """Изменение статуса задачи"""
        task = self.get_object()
        new_status = kwargs.get("status")
        if not new_status:
            return Response(
                {"detail": "Необходим новый статус для задачи."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        valid_statuses = ["backlog", "in_progress", "done", "new"]
        normalized_status = new_status.lower()
        if normalized_status not in valid_statuses:
            return Response(
                {"detail": "Неверный статус."}, status=status.HTTP_400_BAD_REQUEST
            )
        task.status = normalized_status.upper()
        task.save()

        return Response({"detail": "Статус обновлен."}, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_summary="Получение просроченных задач")
    @action(detail=False, methods=["GET"])
    def overdue_tasks(self, _request):
        """Получение просроченных задач"""
        today = timezone.now().date()
        overdue_tasks = Task.objects.filter(
            due_date__lt=today, status__in=["NEW", "BACKLOG", "IN_PROGRESS"]
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Поиск задач по описанию",
        responses={200: TaskSerializer(many=True)},
        parameters=[
            openapi.Parameter(
                "search_term",
                openapi.IN_QUERY,
                description="Термин для поиска в описании задачи",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    @action(detail=False, methods=["GET"], url_path="search")
    def get_search(self, _request):
        """Поиск задач по описанию"""
        queryset = self.get_queryset()
        # Получение задач, которые должны быть выполнены в ближайшие 7 дней
        if "due_soon" in self.request.query_params:
            today = timezone.now().date()
            seven_days_later = today + timedelta(days=7)
            queryset = queryset.filter(
                due_date__gte=today, due_date__lte=seven_days_later
            )

        # Фильтрация задач с высоким приоритетом или с датой выполнения завтра
        if "priority_or_due_tomorrow" in self.request.query_params:
            tomorrow = timezone.now().date() + timedelta(days=1)
            queryset = queryset.filter(Q(priority="5") | Q(due_date=tomorrow))

        # Фильтрация задач, которые не выполнены и имеют высокий приоритет
        if "high_priority" in self.request.query_params:
            queryset = queryset.filter(~Q(status="DONE") & Q(priority="5"))

        # Задачи, которые не принадлежат текущему пользователю и имеют статус
        # "в процессе" или "отменены"
        if "not_assigned_to_user" in self.request.query_params:
            user = self.request.user
            queryset = queryset.filter(
                ~Q(assignee=user) & Q(status__in=["IN_PROGRESS", "CANCELED"])
            )

        # Фильтрация по параметру 'search' (по title или description)
        if "search_term" in self.request.query_params:
            search_term = self.request.query_params.get("search_term", "")
            queryset = queryset.filter(
                Q(name__icontains=search_term) | Q(description__icontains=search_term)
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SubtaskViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с подзадачами"""

    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer

    def get_serializer_class(self):
        """В зависимости от текущего действия выбираем соответствующий сериализатор"""
        return (
            SubtaskCreateSerializer
            if self.action in ["create", "update", "partial_update"]
            else SubtaskSerializer
        )

    @swagger_auto_schema(
        operation_summary="Получение всех подзадач",
        responses={200: SubtaskSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """Отображение подзадач"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание новой подзадачи",
        request_body=SubtaskSerializer,
        responses={201: SubtaskSerializer()},
    )
    def create(self, request, *args, **kwargs):
        """Создание новой подзадачи"""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновление подзадачи",
        request_body=SubtaskSerializer,
        responses={200: SubtaskSerializer()},
    )
    def update(self, request, *args, **kwargs):
        """Обновление подзадачи"""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление подзадачи",
        request_body=SubtaskSerializer,
        responses={200: SubtaskSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        """Чстичное обновление подзадачи"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление подзадачи", responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        """Удаление подзадачи"""
        return super().destroy(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с комментариями"""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    @swagger_auto_schema(
        operation_summary="Получение всех комментариев",
        responses={200: CommentSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        """Отображение комментариев"""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание нового комментария",
        request_body=CommentSerializer,
        responses={201: CommentSerializer()},
    )
    def create(self, request, *args, **kwargs):
        """Создание нового комментария"""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновление комментария",
        request_body=CommentSerializer,
        responses={200: CommentSerializer()},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление комментария",
        request_body=CommentSerializer,
        responses={200: CommentSerializer()},
    )
    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление комментария"""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удаление комментария", responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        """Удаление комментария"""
        return super().destroy(request, *args, **kwargs)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Неверное имя пользователя или пароль"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.auth
        if token:
            token.delete()
            return Response(
                {"message": "Вы успешно вышли из системы"}, status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Вы не авторизованы"}, status=status.HTTP_400_BAD_REQUEST
        )
