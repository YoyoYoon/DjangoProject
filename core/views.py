from datetime import datetime, timedelta
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, ProjectForm, TaskForm, CalendarEventForm, UserProfileForm, HabitForm
from .models import Project, Task, CalendarEvent, UserProfile, Habit
from django.http import JsonResponse
import json
from .validations import validate_project_owner
import calendar
from django.contrib import messages


# Create your views here.


# Home & User Management Views
class HomeView(TemplateView):
    template_name = 'core/home.html'


class RegisterView(CreateView):
    model = UserProfile
    form_class = UserRegistrationForm
    template_name = 'core/register.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        try:
            user = form.save()
            login(self.request, user)
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, f"Unexpected error: {e}")
            return self.form_invalid(form)


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'core/edit_profile.html'
    success_url = reverse_lazy('profile_detail')

    def get_object(self, queryset=None):
        return self.request.user.userprofile


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'core/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'


# Project Views
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'core/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'core/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.object.tasks.all()
        return context


class CreateProjectView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'core/project_form.html'
    success_url = reverse_lazy('project_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, f"Unexpected error: {e}")
            return self.form_invalid(form)


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'core/project_form.html'
    success_url = reverse_lazy('project_list')

    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, f"Unexpected error: {e}")
            return self.form_invalid(form)


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'core/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"Error deleting project: {e}")
            return redirect('project_list')

@login_required
def projects_json(request):
    projects = Project.objects.filter(owner=request.user)
    data = []
    for project in projects:
        data.append({
            'id': project.id,
            'title': project.title,
            'created_at': project.created_at.isoformat(),
            'due_date': project.due_date.isoformat() if project.due_date else project.created_at.isoformat()
        })
    return JsonResponse(data, safe=False)



# Task Views
class AddTaskView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'core/task_form.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.project = validate_project_owner(request.user, self.kwargs['project_id'])
        except ValidationError:
            messages.error(request, "You cannot add tasks to this project.")
            return redirect('project_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.project = self.project
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, f"Unexpected error: {e}")
            return self.form_invalid(form)

    def get_success_url(self):
        return redirect('project_detail', pk=self.project.pk).url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = self.project
        return context


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'core/task_form.html'

    def test_func(self):
        task = self.get_object()
        return task.project.owner == self.request.user

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, f"Unexpected error: {e}")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.project.pk})


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'core/task_confirm_delete.html'

    def test_func(self):
        task = self.get_object()
        return task.project.owner == self.request.user

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.project.pk})

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"Error deleting task: {e}")
            return redirect('project_detail', pk=self.get_object().project.pk)


class ToggleTaskDoneView(LoginRequiredMixin, View):
    def post(self, request, pk):
        try:
            task = get_object_or_404(Task, id=pk, project__owner=request.user)
            data = json.loads(request.body)
            done = data.get('done', False)
            task.status = 'completed' if done else 'pending'
            task.save()
            return JsonResponse({'status': 'success', 'new_status_display': task.get_status_display()})
        except ValidationError as e:
            errors = getattr(e, 'message_dict', str(e))
            return JsonResponse({'status': 'error', 'errors': errors}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


#calendar and events views
@login_required()
def calendar_view(request):
    try:
        projects = Project.objects.filter(owner=request.user)
        events = []
        for project in projects:
            if project.due_date:
                events.append({
                    'title': project.title,
                    'start': project.created_at.date().isoformat(),
                    'end': project.due_date.isoformat(),
                    'color': '#3788d8'
                })
        events_json = json.dumps(events)
        form = CalendarEventForm()
        return render(request, 'core/calendar.html', {'form': form, 'events_json': events_json})
    except Exception as e:
        messages.error(request, f"Error loading calendar: {e}")
        return redirect('dashboard')

@login_required
def calendar_events_json(request):
    events = CalendarEvent.objects.filter(user=request.user)
    data = []

    start_param = request.GET.get('start')  # e.g., "2025-08-01"
    end_param = request.GET.get('end')      # e.g., "2025-08-31"
    view_start = datetime.fromisoformat(start_param) if start_param else None
    view_end = datetime.fromisoformat(end_param) if end_param else None

    for event in events:
        data.append({
            'id': str(event.id),
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat() if event.end_time else None,
            'allDay': event.all_day,
            'description': event.description,
            'repeat': event.repeat,
        })

        # repeated events
        if event.repeat != 'none' and event.repeat_until:
            current_start = event.start_time
            current_end = event.end_time
            repeat_until = event.repeat_until

            occurrence_count = 0
            MAX_OCCURRENCES = 100

            while True:
                if event.repeat == 'daily':
                    current_start += timedelta(days=1)
                    if current_end:
                        current_end += timedelta(days=1)
                elif event.repeat == 'weekly':
                    current_start += timedelta(weeks=1)
                    if current_end:
                        current_end += timedelta(weeks=1)
                elif event.repeat == 'monthly':
                    month = current_start.month + 1
                    year = current_start.year
                    if month > 12:
                        month = 1
                        year += 1
                    last_day = calendar.monthrange(year, month)[1]
                    day = min(current_start.day, last_day)
                    current_start = current_start.replace(year=year, month=month, day=day)

                    if current_end:
                        month_end = current_end.month + 1
                        year_end = current_end.year
                        if month_end > 12:
                            month_end = 1
                            year_end += 1
                        last_day_end = calendar.monthrange(year_end, month_end)[1]
                        day_end = min(current_end.day, last_day_end)
                        current_end = current_end.replace(year=year_end, month=month_end, day=day_end)

                occurrence_count += 1
                if occurrence_count > MAX_OCCURRENCES:
                    break

                if current_start.date() > repeat_until:
                    break

                if view_end and current_start > view_end:
                    break

                if view_start and current_start < view_start:
                    continue

                # Add repeated occurrence
                data.append({
                    'id': f"{event.id}-{current_start.date()}",
                    'title': event.title,
                    'start': current_start.isoformat(),
                    'end': current_end.isoformat() if current_end else None,
                    'allDay': event.all_day,
                    'description': event.description,
                    'repeat': event.repeat,
                })

    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
def add_event(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)
    try:
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            return JsonResponse({'status': 'success', 'id': event.id})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    except ValidationError as e:
        return JsonResponse({'status': 'error', 'errors': e.message_dict}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@login_required
def update_event(request, event_id):
    event = get_object_or_404(CalendarEvent, id=event_id)

    if request.method == 'GET':
        return JsonResponse({
            'title': event.title,
            'description': event.description,
            'start_time': event.start_time.strftime('%Y-%m-%dT%H:%M'),
            'end_time': event.end_time.strftime('%Y-%m-%dT%H:%M') if event.end_time else '',
            'all_day': event.all_day,
            'repeat': event.repeat,
            'repeat_until': event.repeat_until.strftime('%Y-%m-%dT%H:%M') if event.repeat_until else '',
        })

    elif request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
    try:
        form = CalendarEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    except ValidationError as e:
        return JsonResponse({'status': 'error', 'errors': e.message_dict}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@login_required
def delete_event(request, event_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
    try:
        event = get_object_or_404(CalendarEvent, pk=event_id, user=request.user)
        event.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def event_detail(request, event_id):
    try:
        event = get_object_or_404(CalendarEvent, pk=event_id, user=request.user)
        data = {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat() if event.end_time else None,
            'allDay': event.all_day,
            'repeat': event.repeat,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


#Habit views
class HabitListView(LoginRequiredMixin, ListView):
    model = Habit
    template_name = 'core/habit_list.html'
    context_object_name = 'habits'

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user, active=True).order_by('title')

class HabitCreateView(LoginRequiredMixin, CreateView):
    model = Habit
    form_class = HabitForm
    template_name = 'core/habit_form.html'
    success_url = reverse_lazy('habit-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, "Unexpected error: " + str(e))
            return self.form_invalid(form)

class HabitUpdateView(LoginRequiredMixin, UpdateView):
    model = Habit
    form_class = HabitForm
    template_name = 'core/habit_form.html'
    success_url = reverse_lazy('habit-list')

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception as e:
            form.add_error(None, "Unexpected error: " + str(e))
            return self.form_invalid(form)

@login_required
def habits_json(request):
    habits = Habit.objects.filter(user=request.user, active=True)
    data = []

    start_param = request.GET.get('start')
    end_param = request.GET.get('end')
    view_start = datetime.fromisoformat(start_param) if start_param else None
    view_end = datetime.fromisoformat(end_param) if end_param else None

    for habit in habits:
        current_date = habit.start_date
        end_date = habit.end_date or habit.start_date  # If no end date, treat as single day

        # Generate occurrences according to repeat
        while current_date <= end_date:
            # Skip if outside view range
            if view_end and current_date > view_end.date():
                break
            if view_start and current_date < view_start.date():
                current_date += timedelta(days=1) if habit.repeat in ['daily','none'] else timedelta(weeks=1)
                continue

            data.append({
                'id': f"habit-{habit.id}-{current_date}",
                'title': habit.title,
                'start': datetime.combine(current_date, datetime.min.time()).isoformat(),
                'end': datetime.combine(current_date, datetime.min.time()).isoformat(),
                'allDay': True,
                'description': habit.description,
                'repeat': habit.repeat,
                'type': 'habit'
            })

            if habit.repeat == 'daily':
                current_date += timedelta(days=1)
            elif habit.repeat == 'weekly':
                current_date += timedelta(weeks=1)
            elif habit.repeat == 'monthly':
                month = current_date.month + 1
                year = current_date.year
                if month > 12:
                    month = 1
                    year += 1
                last_day = calendar.monthrange(year, month)[1]
                day = min(current_date.day, last_day)
                current_date = current_date.replace(year=year, month=month, day=day)
            else:
                break

    return JsonResponse(data, safe=False)