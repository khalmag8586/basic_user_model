from django.db import models
from django.conf import settings
import uuid


class Event(models.Model):
    event_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="events", null=True
    )
    color_category = models.CharField(max_length=20, blank=True, null=True)
    recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(max_length=255, blank=True, null=True)
    reminder_settings = models.JSONField(blank=True, null=True)
