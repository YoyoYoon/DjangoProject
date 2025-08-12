from datetime import timezone

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from core.models import Project, Task, CalendarEvent


def validate_event_times(start_time, end_time):
    if start_time >= end_time:
        raise ValidationError("End time must be after start time.")

def validate_not_in_past(start_time):
    if start_time < now():
        raise ValidationError("Start time cannot be in the past.")

def validate_project_owner(user, project_id):
    return get_object_or_404(Project, id=project_id, owner=user)

def validate_task_owner(user, task_id):
    return get_object_or_404(Task, id=task_id, project__owner=user)

def validate_event_owner(user, event_id):
    return get_object_or_404(CalendarEvent, id=event_id, user=user)

def require_post(request):
    if request.method != 'POST':
        from django.http import JsonResponse
        return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)
    return None
