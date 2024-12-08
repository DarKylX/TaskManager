from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from django.urls import path, include

# Импортируем все необходимые viewsets
from .views.view_sets import (
    TaskViewSet,
    ProjectViewSet,
    SubtaskViewSet,
    CommentViewSet,
    UserProfileViewSet,
    UserBIOViewSet,
    UserProfileProjectViewSet
)

router = DefaultRouter()


router.register(r'task', TaskViewSet)
router.register(r'project', ProjectViewSet)
router.register(r'subtask', SubtaskViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'userprofile', UserProfileViewSet)
router.register(r'userbio', UserBIOViewSet)
router.register(r'userprofileproject', UserProfileProjectViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('task/status/<str:status>/', TaskViewSet.as_view({'get': 'list'})),
    path('task/<int:pk>/history/', TaskViewSet.as_view({'get': 'history'}), name='task-history'),
    path('task/<int:pk>/change_status/', TaskViewSet.as_view({'post': 'change_status'}), name='task-change-status')

]
