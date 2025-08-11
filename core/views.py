
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, ProjectForm, TaskForm, CalendarEventForm, UserProfileForm
from .models import Project, Task, CalendarEvent, UserProfile
from django.http import JsonResponse



# Create your views here.
class HomeView(TemplateView):
    template_name = 'core/home.html'

class AboutView(TemplateView):
    template_name = 'core/about.html'


class RegisterView(View):
    form_class = UserRegistrationForm
    template_name = 'core/register.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, self.template_name, {'form': form})


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
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile



class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'


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
        # restrict access to only owner projects
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
        return super().form_valid(form)


class AddTaskView(LoginRequiredMixin, View):
    form_class = TaskForm
    template_name = 'core/task_form.html'

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'project': project})

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        form = self.form_class(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            return redirect('project_detail', pk=project.id)
        return render(request, self.template_name, {'form': form, 'project': project})

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'core/project_form.html'
    success_url = reverse_lazy('project_list')

    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user

class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'core/project_confirm_delete.html'
    success_url = reverse_lazy('project_list')

    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user

class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'core/task_form.html'

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.project.pk})

    def test_func(self):
        task = self.get_object()
        return task.project.owner == self.request.user

class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    template_name = 'core/task_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('project_detail', kwargs={'pk': self.object.project.pk})

    def test_func(self):
        task = self.get_object()
        return task.project.owner == self.request.user


@login_required
def calendar_view(request):
    form = CalendarEventForm()
    return render(request, 'core/calendar.html', {'form': form})

@login_required
def calendar_events_json(request):
    events = CalendarEvent.objects.filter(user=request.user)
    data = []
    for event in events:
        data.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat() if event.end_time else None,
            'allDay': event.all_day,
            'description': event.description,
            'repeat': event.repeat,
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@login_required
def add_event(request):
    if request.method == 'POST':
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            return JsonResponse({'status': 'success', 'id': event.id})
        else:
            print("FORM ERRORS:", form.errors)  # debug
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)


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
            'repeat': event.repeat
        })

    elif request.method == "POST":
        form = CalendarEventForm(request.POST, instance=event)

        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


@csrf_exempt
@login_required
def delete_event(request, event_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
    event = get_object_or_404(CalendarEvent, pk=event_id, user=request.user)
    event.delete()
    return JsonResponse({'status': 'success'})


@login_required
def event_detail(request, event_id):
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