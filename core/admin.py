from django.contrib import admin
from .models import UserProfile, Project, Task, ProgressLog

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at', 'due_date')
    list_filter = ('created_at', 'due_date')
    search_fields = ('title', 'description')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority')
    search_fields = ('title',)

@admin.register(ProgressLog)
class ProgressLogAdmin(admin.ModelAdmin):
    list_display = ('project', 'date')
    search_fields = ('project__title', 'content')
