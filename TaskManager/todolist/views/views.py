from django.utils import timezone
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden, JsonResponse
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
from ..models import Project, Task, Comment, UserProfile, UserProfileProject
from ..serializers.RegisterSerializer import RegisterSerializer
from datetime import datetime

from django import template

register = template.Library()


@register.filter(name='strip')
def strip_spaces(value):
    return value.strip()


# API Views
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'auth/register.html')

    def post(self, request):
        if request.content_type == 'application/json':
            # API запрос
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    "token": token.key,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Веб-форма запрос
            serializer = RegisterSerializer(data=request.POST)
            if serializer.is_valid():
                user = serializer.save()
                login(request, user)
                messages.success(request, 'Регистрация успешна!')
                return redirect('dashboard')
            else:
                for error in serializer.errors.values():
                    messages.error(request, error[0])
                return render(request, 'auth/register.html')


@csrf_exempt
def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('login')


class LoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Обработка GET-запроса для отображения формы входа
        return render(request, 'auth/login.html')

    def post(self, request):
        # Проверяем, пришел ли запрос от веб-формы или API
        if request.content_type == 'application/json':
            # API запрос
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(username=username, password=password)

            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    "token": token.key,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                })
            return Response(
                {"error": "Неверное имя пользователя или пароль"},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # Веб-форма запрос
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                messages.success(request, 'Вы успешно вошли в систему')
                return redirect('dashboard')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
                return render(request, 'auth/login.html')


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.auth:
            request.auth.delete()
            return Response({"message": "Вы успешно вышли из системы"})
        return Response({"error": "Вы не авторизованы"}, status=status.HTTP_400_BAD_REQUEST)


# Web Views
@login_required
def dashboard(request):
    context = {
        'projects': Project.objects.filter(members=request.user),
        'tasks': Task.objects.filter(assignee=request.user),
        'users': UserProfile.objects.all().order_by('username'),  # или order_by('first_name')
        'task_statuses': dict(Task.STATUS_CHOICES),
        'task_priorities': dict(Task.PRIORITY_CHOICES),
        'project_statuses': dict(Project.STATUS_CHOICES),
        'today': timezone.now().date(),

    }
    return render(request, 'dashboard/dashboard.html', context)



@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, members=request.user)
    tasks = Task.objects.filter(project=project)
    project_members = UserProfileProject.objects.filter(project=project)
    return render(request, 'dashboard/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'project_members': project_members,
    })


@login_required
def add_comment(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        if comment_text:
            comment = Comment.objects.create(
                task=task,
                author=request.user,
                text=comment_text
            )
            messages.success(request, 'Комментарий успешно добавлен!')
            return redirect('task_detail', pk=task.id)
    return redirect('task_detail', pk=task.id)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        return HttpResponseForbidden("Вы не можете удалить этот комментарий")
    comment.delete()
    messages.success(request, "Комментарий успешно удален")
    return redirect('task_detail', pk=comment.task.id)


def create_project(request):
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            name = request.POST.get('name')
            description = request.POST.get('description')
            status = request.POST.get('status')
            members = request.POST.getlist('members')  # Убрал '[]' из members[]

            # Проверяем обязательные поля
            if not all([name, description, status]):
                messages.error(request, 'Все обязательные поля должны быть заполнены')
                return redirect('dashboard')

            # Создаем проект
            project = Project.objects.create(
                name=name,
                description=description,
                status=status
            )

            # Добавляем участников
            project.members.add(request.user)  # Добавляем создателя проекта
            if members:  # Проверяем, есть ли дополнительные участники
                project.members.add(*members)

            messages.success(request, 'Проект успешно создан')
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f'Ошибка при создании проекта: {str(e)}')
            return redirect('dashboard')

    return redirect('dashboard')


@login_required
def create_task(request):
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            name = request.POST.get('name')
            description = request.POST.get('description')
            status = request.POST.get('status')
            priority = request.POST.get('priority')
            project_id = request.POST.get('project')
            assignee_id = request.POST.get('assignee')
            due_date = request.POST.get('due_date')
            category = request.POST.get('category')

            # Проверяем обязательные поля (кроме assignee, он может быть пустым)
            if not all([name, description, status, priority, project_id, due_date, category]):
                messages.error(request, 'Все обязательные поля должны быть заполнены')
                return redirect('dashboard')

            # Преобразуем строку даты в объект date
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()

            # Проверяем, что дата не в прошлом
            if due_date < timezone.now().date():
                messages.error(request, 'Дата выполнения не может быть в прошлом')
                return redirect('dashboard')

            # Проверяем уникальность названия задачи для пользователя
            if Task.objects.filter(name=name, assignee_id=assignee_id).exists():
                messages.error(request, 'У вас уже есть задача с таким названием')
                return redirect('dashboard')

            # Создаем задачу
            task = Task(
                name=name,
                description=description,
                status=status,
                priority=priority,
                project_id=project_id,
                assignee_id=assignee_id,
                due_date=due_date,
                category=category
            )

            # Вызываем полную валидацию модели
            task.full_clean()

            # Сохраняем задачу
            task.save()

            response = redirect('task_detail', pk=task.id)
            messages.success(request, 'Задача успешно создана')
            return response

        except ValidationError as e:
            # Обрабатываем ошибки валидации из модели
            error_messages = []
            for field, errors in e.message_dict.items():
                error_messages.extend(errors)
            messages.error(request, f'Ошибка валидации: {", ".join(error_messages)}')
            return redirect('dashboard')

        except Exception as e:
            messages.error(request, f'Ошибка при создании задачи: {str(e)}')
            return redirect('dashboard')

    return redirect('dashboard')

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Проверка прав доступа
    if not (task.assignee == request.user or task.project.members.filter(pk=request.user.pk).exists()):
        messages.error(request, 'У вас нет доступа к этой задаче')
        return redirect('dashboard')

    # Обновление данных задачи через POST-запрос
    if request.method == 'POST':
        task.description = request.POST.get('description').strip()
        task.status = request.POST.get('status')
        task.assignee = UserProfile.objects.get(pk=request.POST.get('assigned_to'))
        task.project = Project.objects.get(pk=request.POST.get('project'))
        task.due_date = request.POST.get('deadline')
        task.save()
        messages.success(request, 'Задача успешно обновлена!')

    # Передача контекста
    projects = Project.objects.filter(members=request.user)
    users = UserProfile.objects.all()
    return render(request, 'dashboard/task_detail.html', {
        'task': task,
        'projects': projects,
        'users': users
    })


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, assignee=request.user)
    project_id = task.project.id
    task.delete()
    messages.success(request, 'Задача успешно удалена!')
    return redirect('project_detail', pk=project_id)

@login_required
def add_member(request, project_id):
    project = get_object_or_404(Project, pk=project_id, members=request.user)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(UserProfile, pk=user_id)
        UserProfileProject.objects.create(project=project, user_profile=user)
        messages.success(request, 'Участник успешно добавлен в проект.')
        return redirect('project_detail', pk=project_id)
    users = UserProfile.objects.exclude(id__in=project.members.all())
    return render(request, 'dashboard/add_member.html', {'project': project, 'users': users})

@login_required
def remove_member(request, project_id, user_id):
    project = get_object_or_404(Project, pk=project_id, members=request.user)
    user = get_object_or_404(UserProfile, pk=user_id)
    UserProfileProject.objects.filter(project=project, user_profile=user).delete()
    messages.success(request, 'Участник успешно удален из проекта.')
    return redirect('project_detail', pk=project_id)
