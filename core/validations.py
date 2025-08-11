from django.core.exceptions import ValidationError
from django.utils.timezone import now

def validate_event_times(start_time, end_time):
    if start_time >= end_time:
        raise ValidationError("End time must be after start time.")

def validate_not_in_past(start_time):
    if start_time < now():
        raise ValidationError("Start time cannot be in the past.")
