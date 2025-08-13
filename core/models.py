from datetime import datetime, time
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import localdate
from core.validations import validate_not_in_past

# Extend User
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.user.username


class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    #due date validation
    def clean(self):
        if self.due_date and self.created_at and self.due_date < self.created_at.date():
            raise ValidationError("Project due date cannot be before the creation date.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_done = models.BooleanField(default=False)  #   for checkbox

    #past-date validation
    def clean(self):
        if self.due_date and self.due_date < timezone.now().date():
            raise ValidationError("Task due date cannot be in the past.")

    def save(self, *args, **kwargs):

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.status})"


class CalendarEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    all_day = models.BooleanField(default=False)

    REPEAT_CHOICES = [
        ('none', 'Does not repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    repeat = models.CharField(max_length=10, choices=REPEAT_CHOICES, default='none', blank=True)
    repeat_until = models.DateField(null=True, blank=True)

    def clean(self):
        # ensure end_time is after start_time
        if self.end_time and self.start_time > self.end_time:
            raise ValidationError("End time cannot be before start time.")

        # Ensure repeat_until is after start_time
        if self.repeat != 'none' and self.repeat_until:
            repeat_until_dt = datetime.combine(self.repeat_until, time.min)
            if repeat_until_dt < self.start_time:
                raise ValidationError("Repeat until date cannot be before start date.")

        # ensure start_time is not in the past
        validate_not_in_past(self.start_time)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.start_time} - {self.end_time if self.end_time else 'No end'})"


class Habit(models.Model):
    REPEAT_CHOICES = [
        ('none', 'Does not repeat'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='habits')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    repeat = models.CharField(max_length=10, choices=REPEAT_CHOICES, default='daily')
    active = models.BooleanField(default=True)

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError("Habit end date cannot be before start date.")
        if self.start_date < localdate():
            raise ValidationError("Start date cannot be in the past.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.repeat})"


