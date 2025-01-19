# todolist/web_urls.py (новый файл для веб-маршрутов)
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import views  # основные view функции
from .views.views import RegisterView, dashboard, project_detail, task_detail, create_project, create_task

urlpatterns = [
    # Аутентификация
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    # Основные страницы
    path('', views.dashboard, name='dashboard'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),

    # CRUD операции
    path('project/<int:pk>/update/', views.update_project, name='update_project'),
    path('task/<int:pk>/update/', views.update_task, name='update_task'),
    path('project/create/', views.create_project, name='create_project'),
    path('create-project/', views.create_project, name='create_project'),
    path('create-task/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/add-comment/', views.add_comment, name='add_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('tasks/<int:pk>/delete/', views.delete_task, name='delete_task'),
    path('project/<int:project_id>/add_member/', views.add_member, name='add_member'),
    path('project/<int:project_id>/remove-member/<int:user_id>/', views.remove_member, name='remove_member'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('subtask/<int:subtask_id>/update/', views.update_subtask, name='update_subtask'),
    path('subtask/<int:subtask_id>/delete/', views.delete_subtask, name='delete_subtask'),
]