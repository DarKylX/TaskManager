from django.contrib import admin
from .models import UserProfile, UserBIO, Project, UserProfileProject, Task, Subtask, Comment

class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'status', 'priority', 'due_date')
    search_fields = ('name', 'description')
    list_filter = ('status', 'priority')

admin.site.register(Task, TaskAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'email', 'is_staff', 'is_active')
    search_fields = ('nickname', 'email')

admin.site.register(UserProfile, UserProfileAdmin)

class UserBIOAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'age', 'user')
    search_fields = ('full_name', 'user__nickname')

admin.site.register(UserBIO, UserBIOAdmin)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('name', 'description')

admin.site.register(Project, ProjectAdmin)


class UserProfileProjectAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'project')
    search_fields = ('user_profile__nickname', 'project__name')

admin.site.register(UserProfileProject, UserProfileProjectAdmin)


class SubtaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'task')
    list_filter = ('status', 'task')
    search_fields = ('name',)

admin.site.register(Subtask, SubtaskAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'task', 'created_at')
    search_fields = ('text', 'task__name', 'author__nickname')

admin.site.register(Comment, CommentAdmin)
