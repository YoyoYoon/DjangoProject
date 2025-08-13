from django.contrib import admin
from .models import UserProfile, Project, Task, CalendarEvent, Habit


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ['title', 'status', 'priority', 'due_date', 'is_done']
    readonly_fields = []
    show_change_link = True


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'created_at', 'due_date']
    list_filter = ['due_date', 'owner']
    search_fields = ['title', 'description', 'owner__username']
    ordering = ['-created_at']
    inlines = [TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'due_date', 'is_done']
    list_filter = ['status', 'priority', 'due_date', 'project']
    search_fields = ['title', 'description', 'project__title']
    ordering = ['due_date']


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'start_time', 'end_time', 'all_day', 'repeat', 'repeat_until']
    list_filter = ['all_day', 'repeat', 'user']
    search_fields = ['title', 'description', 'user__username']
    ordering = ['-start_time']
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description')
        }),
        ('Timing', {
            'fields': ('start_time', 'end_time', 'all_day')
        }),
        ('Repeat Options', {
            'fields': ('repeat', 'repeat_until'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'start_date', 'end_date', 'repeat', 'active']
    list_filter = ['repeat', 'active', 'user']
    search_fields = ['title', 'description', 'user__username']
    ordering = ['-start_date']
    fieldsets = (
        (None, {
            'fields': ('user', 'title', 'description', 'active')
        }),
        ('Timing', {
            'fields': ('start_date', 'end_date')
        }),
        ('Repeat Options', {
            'fields': ('repeat',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'profile_picture']
    search_fields = ['user__username', 'bio']

