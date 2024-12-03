from rest_framework import serializers
from TaskManager.todolist.models import UserProfile, UserBIO, Project, UserProfileProject, Task, Subtask, Comment
from django.utils import timezone



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'



class UserBiosSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBIO
        fields = '__all__'



class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'



class UserProfileProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileProject
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'



class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = '__all__'



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
