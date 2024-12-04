from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter

from .views.view_sets import TaskViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'task', TaskViewSet)

urlpatterns = [
    path('',  include(router.urls))
]
