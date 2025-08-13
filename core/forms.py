from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.timezone import localdate

from core.models import Project, Task, CalendarEvent, UserProfile, Habit
from core.validations import validate_event_times, validate_not_in_past


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your personal goals...'}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'due_date']
        widgets= {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TaskCompleteForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['is_done']


class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['title', 'description', 'start_time', 'end_time', 'all_day', 'repeat', 'repeat_until']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make 'repeat' field optional so default='none' can be used if not provided
        self.fields['repeat'].required = False

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            validate_event_times(start_time, end_time)
            validate_not_in_past(start_time)

        return cleaned_data

    def clean_repeat_until(self):
        repeat_until = self.cleaned_data.get('repeat_until')
        if repeat_until and repeat_until < self.cleaned_data.get('start_time').date():
            raise forms.ValidationError("Repeat until cannot be before start date")
        return repeat_until


class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['title', 'description', 'start_date', 'end_date', 'repeat', 'active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial start_date to today
        if not self.instance.pk:
            self.instance.start_date = localdate()