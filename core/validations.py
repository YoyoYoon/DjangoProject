from datetime import datetime, date, time
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone

# Ensure event ends after it starts
def validate_event_times(start_time, end_time):
    if start_time >= end_time:
        raise ValidationError("End time must be after start time.")

# Ensure start date is today or later
def validate_not_in_past(dt):
    now = timezone.now()
    if isinstance(dt, datetime):
        if dt < now:
            raise ValidationError("Start time cannot be in the past.")
    elif isinstance(dt, date):
        today = datetime.combine(date.today(), time.min)
        if datetime.combine(dt, time.min) < today:
            raise ValidationError("Date cannot be in the past.")

# Check the user owns the project
def validate_project_owner(user, project_id):
    from core.models import Project
    return get_object_or_404(Project, id=project_id, owner=user)

# Check the user owns the task
def validate_task_owner(user, task_id):
    from core.models import Task
    return get_object_or_404(Task, id=task_id, project__owner=user)

# Check the user owns the calendar event
def validate_event_owner(user, event_id):
    from core.models import CalendarEvent
    return get_object_or_404(CalendarEvent, id=event_id, user=user)

def require_post(request):
    if request.method != 'POST':
        from django.http import JsonResponse
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
    return None
