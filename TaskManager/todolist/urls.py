""" Урлы """

from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Импортируем все необходимые viewsets
from .views.view_sets import (CommentViewSet, ProjectViewSet, SubtaskViewSet,
                              TaskViewSet, UserBIOViewSet,
                              UserProfileProjectViewSet, UserProfileViewSet, index,
                              task_summary, RegisterView,
                              LoginView, LogoutView)

router = DefaultRouter()


router.register(r"task", TaskViewSet)
router.register(r"project", ProjectViewSet)
router.register(r"subtask", SubtaskViewSet)
router.register(r"comment", CommentViewSet)
router.register(r"userprofile", UserProfileViewSet)
router.register(r"userbio", UserBIOViewSet)
router.register(r"userprofileproject", UserProfileProjectViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("task/status/<str:status>/", TaskViewSet.as_view({"get": "list"})),
    path(
        "task/<int:pk>/history/",
        TaskViewSet.as_view({"get": "history"}),
        name="task-history",
    ),
    path(
        "task/<int:pk>/change_status/<str:status>",
        TaskViewSet.as_view({"post": "change_status"}),
        name="task-change-status",
    ),
    path(
        "project/<int:pk>/",
        ProjectViewSet.as_view({"get": "retrieve"}),
        name="project_detail",
    ),
]
