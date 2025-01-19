import os

from django.db.models import Q
from django.db.models.functions import Lower
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..forms import UserProfileForm, UserBIOForm, SubtaskForm
from ..models import (
    Project,
    Task,
    Comment,
    UserProfile,
    UserProfileProject,
    UserBIO,
    Subtask,
)
from ..serializers.RegisterSerializer import RegisterSerializer
from datetime import datetime

from django import template

register = template.Library()


@register.filter(name="strip")
def strip_spaces(value):
    return value.strip()


# API Views
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, "auth/register.html")

    def post(self, request):
        if request.content_type == "application/json":
            # API запрос
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        "token": token.key,
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Веб-форма запрос
            serializer = RegisterSerializer(data=request.POST)
            if serializer.is_valid():
                user = serializer.save()
                login(request, user)
                messages.success(request, "Регистрация успешна!")
                return redirect("dashboard")
            else:
                for error in serializer.errors.values():
                    messages.error(request, error[0])
                return render(request, "auth/register.html")


@csrf_exempt
def logout_view(request):
    logout(request)
    messages.success(request, "Вы успешно вышли из системы")
    return redirect("login")


class LoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Обработка GET-запроса для отображения формы входа
        return render(request, "auth/login.html")

    def post(self, request):
        # Проверяем, пришел ли запрос от веб-формы или API
        if request.content_type == "application/json":
            # API запрос
            username = request.data.get("username")
            password = request.data.get("password")
            user = authenticate(username=username, password=password)

            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        "token": token.key,
                        "user": {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                        },
                    }
                )
            return Response(
                {"error": "Неверное имя пользователя или пароль"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            # Веб-форма запрос
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                messages.success(request, "Вы успешно вошли в систему")
                return redirect("dashboard")
            else:
                messages.error(request, "Неверное имя пользователя или пароль")
                return render(request, "auth/login.html")


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.auth:
            request.auth.delete()
            return Response({"message": "Вы успешно вышли из системы"})
        return Response(
            {"error": "Вы не авторизованы"}, status=status.HTTP_400_BAD_REQUEST
        )


# Web Views
@login_required
def dashboard(request):
    search_query = request.GET.get("search", "")
    # Получаем все задачи
    tasks = Task.objects.filter(assignee=request.user).select_related(
        "project", "assignee"
    )

    if search_query:
        tasks = tasks.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    context = {
        "projects": Project.objects.filter(members=request.user).prefetch_related(
            "members"
        ),
        "tasks": tasks,
        "users": UserProfile.objects.all().order_by("username"),
        "task_statuses": dict(Task.STATUS_CHOICES),
        "task_priorities": dict(Task.PRIORITY_CHOICES),
        "project_statuses": dict(Project.STATUS_CHOICES),
        "today": timezone.now().date(),
        "search_query": search_query,
    }

    return render(request, "dashboard/dashboard.html", context)


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, members=request.user)
    context = {
        "project": project,
        "tasks": Task.objects.filter(project=project),
        "project_members": project.members.all(),
        "users": UserProfile.objects.exclude(
            userprofileproject__project=project
        ),  # Доступные пользователи
        "project_statuses": dict(Project.STATUS_CHOICES),
        "task_statuses": dict(Task.STATUS_CHOICES),
        "task_priorities": dict(Task.PRIORITY_CHOICES),
    }
    return render(request, "dashboard/project_detail.html", context)


@login_required
def update_project(request, pk):
    project = get_object_or_404(Project, pk=pk, members=request.user)
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        status = request.POST.get("status")

        if not all([name, description, status]):
            messages.error(request, "Все обязательные поля должны быть заполнены")
            return redirect("project_detail", pk=pk)

        try:
            project.name = name
            project.description = description.strip()
            project.status = status
            project.save()
            messages.success(request, "Проект успешно обновлен")

        except Exception as e:
            messages.error(request, f"Ошибка при обновлении проекта: {str(e)}")

    return redirect("project_detail", pk=pk)


@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, pk=task_id, project__members=request.user)
    if request.method == "POST":
        text = request.POST.get("comment_text").strip()
        if text:
            Comment.objects.create(task=task, author=request.user, text=text)
            messages.success(request, "Комментарий добавлен")
        else:
            messages.error(request, "Текст комментария не может быть пустым")
    return redirect("task_detail", pk=task_id)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    task_id = comment.task.id
    comment.delete()
    messages.success(request, "Комментарий удален")
    return redirect("task_detail", pk=task_id)


def create_project(request):
    if request.method == "POST":
        try:
            # Получаем данные из формы
            name = request.POST.get("name")
            description = request.POST.get("description")
            status = request.POST.get("status")
            members = request.POST.getlist("members")  # Убрал '[]' из members[]

            # Проверяем обязательные поля
            if not all([name, description, status]):
                messages.error(request, "Все обязательные поля должны быть заполнены")
                return redirect("dashboard")

            # Создаем проект
            project = Project.objects.create(
                name=name, description=description, status=status
            )

            # Добавляем участников
            project.members.add(request.user)  # Добавляем создателя проекта
            if members:  # Проверяем, есть ли дополнительные участники
                project.members.add(*members)

            messages.success(request, "Проект успешно создан")
            return redirect("dashboard")

        except Exception as e:
            messages.error(request, f"Ошибка при создании проекта: {str(e)}")
            return redirect("dashboard")

    return redirect("dashboard")


@login_required
def create_task(request):
    if request.method == "POST":
        try:
            # Получаем данные из формы
            name = request.POST.get("name")
            description = request.POST.get("description")
            status = request.POST.get("status")
            priority = request.POST.get("priority")
            project_id = request.POST.get("project")
            assignee_id = request.POST.get("assignee")
            due_date = request.POST.get("due_date")
            category = request.POST.get("category")

            # Проверяем обязательные поля (кроме assignee, он может быть пустым)
            if not all(
                [name, description, status, priority, project_id, due_date, category]
            ):
                messages.error(request, "Все обязательные поля должны быть заполнены")
                return redirect("dashboard")

            # Преобразуем строку даты в объект date
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()

            # Проверяем, что дата не в прошлом
            if due_date < timezone.now().date():
                messages.error(request, "Дата выполнения не может быть в прошлом")
                return redirect("dashboard")

            # Проверяем уникальность названия задачи для пользователя
            if Task.objects.filter(name=name, assignee_id=assignee_id).exists():
                messages.error(request, "У вас уже есть задача с таким названием")
                return redirect("dashboard")

            # Создаем задачу
            task = Task(
                name=name,
                description=description,
                status=status,
                priority=priority,
                project_id=project_id,
                assignee_id=assignee_id,
                due_date=due_date,
                category=category,
            )

            # Вызываем полную валидацию модели
            task.full_clean()

            # Сохраняем задачу
            task.save()

            response = redirect("task_detail", pk=task.id)
            messages.success(request, "Задача успешно создана")
            return response

        except ValidationError as e:
            # Обрабатываем ошибки валидации из модели
            error_messages = []
            for field, errors in e.message_dict.items():
                error_messages.extend(errors)
            messages.error(request, f'Ошибка валидации: {", ".join(error_messages)}')
            return redirect("dashboard")

        except Exception as e:
            messages.error(request, f"Ошибка при создании задачи: {str(e)}")
            return redirect("dashboard")

    return redirect("dashboard")


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, project__members=request.user)
    subtasks = task.subtasks.all()
    subtasks_count = subtasks.count()
    has_subtasks = subtasks.exists()
    subtask_names = subtasks.values_list("name", flat=True)

    # Поиск подзадач
    search_query = request.GET.get("search", "")
    if search_query:
        subtasks = subtasks.filter(name__icontains=search_query)

    if request.method == "POST":
        form = SubtaskForm(request.POST)
        if form.is_valid():
            subtask = form.save(commit=False)
            subtask.task = task
            subtask.save()
            messages.success(request, "Подзадача успешно добавлена")
            return HttpResponseRedirect(request.path)
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме")
    else:
        form = SubtaskForm()

    context = {
        "task": task,
        "projects": Project.objects.filter(members=request.user),
        "users": task.project.members.all(),
        "task_statuses": dict(Task.STATUS_CHOICES),
        "task_priorities": dict(Task.PRIORITY_CHOICES),
        "comments": task.comments.all().order_by("-created_at"),
        "subtasks": subtasks,
        "form": form,
        "subtasks_count": subtasks_count,
        "has_subtasks": has_subtasks,
        "subtask_names": subtask_names,
        "history": task.get_history_changes(),
    }
    return render(request, "dashboard/task_detail.html", context)


def update_subtask(request, subtask_id):

    if request.method == "POST":
        status = request.POST.get("status")
        if status:
            Subtask.objects.filter(id=subtask_id).update(status=status)
            messages.success(request, "Статус подзадачи обновлен")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def delete_subtask(request, subtask_id):
    subtask = get_object_or_404(Subtask, id=subtask_id)

    # Используем delete()
    subtask.delete()
    messages.success(request, "Подзадача удалена")

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


@login_required
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk, project__members=request.user)
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        status = request.POST.get("status")
        priority = request.POST.get("priority")
        category = request.POST.get("category")
        due_date = request.POST.get("due_date")
        task.reference_link = request.POST.get("reference_link") or None

        if not all([name, description, status, priority, category, due_date]):
            messages.error(request, "Все обязательные поля должны быть заполнены")
            return redirect("task_detail", pk=pk)

        try:
            # Обработка файла
            if "attachment" in request.FILES:
                if task.attachment:
                    try:
                        os.remove(task.attachment.path)
                    except Exception as e:
                        print(f"Error removing old file: {e}")
                task.attachment = request.FILES["attachment"]
            elif request.POST.get("remove_attachment") and task.attachment:
                try:
                    os.remove(task.attachment.path)
                    task.attachment = None
                except Exception as e:
                    print(f"Error removing file: {e}")

            task.name = name
            task.description = description.strip()
            task.status = status
            task.priority = priority
            task.category = category
            task.due_date = due_date

            assignee_id = request.POST.get("assignee")
            if assignee_id:
                task.assignee = get_object_or_404(UserProfile, pk=assignee_id)

            task.save()
            messages.success(request, "Задача успешно обновлена")

        except Exception as e:
            messages.error(request, f"Ошибка при обновлении задачи: {str(e)}")

        return redirect("task_detail", pk=pk)


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, project__members=request.user)
    project_id = task.project.id
    task.delete()
    messages.success(request, "Задача успешно удалена")
    return redirect("project_detail", pk=project_id)


@login_required
def add_member(request, project_id):
    project = get_object_or_404(Project, pk=project_id, members=request.user)
    if request.method == "POST":
        user_id = request.POST.get("user")  # Форма должна передавать 'user'
        try:
            user = UserProfile.objects.get(pk=user_id)
            if UserProfileProject.objects.filter(
                user_profile=user, project=project
            ).exists():
                messages.warning(
                    request, "Этот пользователь уже является участником проекта."
                )
            else:
                UserProfileProject.objects.create(user_profile=user, project=project)
                messages.success(request, "Участник успешно добавлен.")
        except UserProfile.DoesNotExist:
            messages.error(request, "Пользователь не найден.")
    return redirect("project_detail", pk=project_id)


@login_required
def remove_member(request, project_id, user_id):
    project = get_object_or_404(Project, pk=project_id, members=request.user)
    user = get_object_or_404(UserProfile, pk=user_id)
    UserProfileProject.objects.filter(project=project, user_profile=user).delete()
    messages.success(request, "Участник успешно удален из проекта.")
    return redirect("project_detail", pk=project_id)


@login_required
def profile_settings(request):
    user = request.user
    try:
        bio = user.bio
    except UserBIO.DoesNotExist:
        bio = UserBIO.objects.create(user=user)

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, instance=user)
        bio_form = UserBIOForm(request.POST, request.FILES, instance=bio)

        if profile_form.is_valid() and bio_form.is_valid():
            profile_form.save()
            bio_form.save()
            messages.success(request, "Профиль успешно обновлен")
            return redirect("profile_settings")
    else:
        profile_form = UserProfileForm(instance=user)
        bio_form = UserBIOForm(instance=bio)

    return render(
        request,
        "dashboard/profile_settings.html",
        {"profile_form": profile_form, "bio_form": bio_form},
    )
