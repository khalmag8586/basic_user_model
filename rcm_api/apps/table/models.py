from django.db import models
from django.conf import settings

import uuid


class RCTable(models.Model):
    table_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    table_number = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField()
    chairs = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="user_created_rctable",
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="user_updated_rctable",
        blank=True,
        null=True,
    )
    is_available = models.BooleanField(default=True)
    is_reserved = models.BooleanField(default=False)
