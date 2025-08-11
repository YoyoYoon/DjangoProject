from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    HomeView, AboutView, RegisterView, DashboardView,
    ProjectListView, ProjectDetailView, CreateProjectView, AddTaskView, ProjectUpdateView, ProjectDeleteView,
    TaskUpdateView, TaskDeleteView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('profile/', views.ProfileDetailView.as_view(), name='profile_detail'),

    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('projects/', ProjectListView.as_view(), name='project_list'),
    path('projects/create/', CreateProjectView.as_view(), name='create_project'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:project_id>/tasks/add/', AddTaskView.as_view(), name='add_task'),
    path('projects/<int:pk>/edit/', ProjectUpdateView.as_view(), name='project_edit'),
    path('projects/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),

    path('tasks/<int:pk>/edit/', TaskUpdateView.as_view(), name='task_edit'),
    path('tasks/<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),

    path('calendar/', views.calendar_view, name='calendar'),
    path('api/calendar/events/', views.calendar_events_json, name='calendar_events_json'),
    path('api/calendar/events/create/', views.add_event, name='add_event'),
    path('api/calendar/events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('api/calendar/events/<int:event_id>/update/', views.update_event, name='update_event'),
    path('api/calendar/events/<int:event_id>/delete/', views.delete_event, name='delete_event'),

]



