from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    HomeView, RegisterView, DashboardView,
    ProjectListView, ProjectDetailView, CreateProjectView, AddTaskView, ProjectUpdateView, ProjectDeleteView,
    TaskUpdateView, TaskDeleteView, ToggleTaskDoneView, HabitListView, HabitCreateView, HabitUpdateView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('profile/', views.ProfileDetailView.as_view(), name='profile_detail'),
#project urls
    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/create/', CreateProjectView.as_view(), name='create_project'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/edit/', ProjectUpdateView.as_view(), name='project_edit'),
    path('projects/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),
    path('api/projects/json/', views.projects_json, name='projects-json'),
#task urls
    path('tasks/<int:pk>/edit/', TaskUpdateView.as_view(), name='task_edit'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    path('projects/<int:project_id>/tasks/add/', AddTaskView.as_view(), name='add_task'),
    path('tasks/<int:pk>/toggle_done/', ToggleTaskDoneView.as_view(), name='toggle_task_done'),
#habit urls
    path('habits/', HabitListView.as_view(), name='habit-list'),
    path('habits/create/', HabitCreateView.as_view(), name='habit-create'),
    path('habits/<int:pk>/edit/', HabitUpdateView.as_view(), name='habit-edit'),
    path('api/habits/json/', views.habits_json, name='habits-json'),
#calendar urls
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/calendar/events/', views.calendar_events_json, name='calendar_events_json'),
    path('api/calendar/events/create/', views.add_event, name='add_event'),
    path('api/calendar/events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('api/calendar/events/<int:event_id>/update/', views.update_event, name='update_event'),
    path('api/calendar/events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
]



