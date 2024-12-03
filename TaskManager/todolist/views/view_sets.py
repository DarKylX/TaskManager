from rest_framework import viewsets
from TaskManager.todolist.models import UserProfile, UserBIO, Project, UserProfileProject, Task, Subtask, Comment
from TaskManager.todolist.serializers.todolists import UserProfileSerializer, UserBiosSerializer, ProjectSerializer, UserProfileProjectSerializer, TaskSerializer, SubtaskSerializer, CommentSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserBIOViewSet(viewsets.ModelViewSet):
    queryset = UserBIO.objects.all()
    serializer_class = UserBiosSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class UserProfileProjectViewSet(viewsets.ModelViewSet):
    queryset = UserProfileProject.objects.all()
    serializer_class = UserProfileProjectSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class SubtaskViewSet(viewsets.ModelViewSet):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
