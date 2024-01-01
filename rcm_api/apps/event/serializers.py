from rest_framework import serializers
from apps.event.models import Event


class EventSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_name_ar = serializers.CharField(source="user.name_ar", read_only=True)

    class Meta:
        model = Event
        fields = [
            "event_id",
            "name",
            "start",
            "end",
            "location",
            "description",
            "color_category",
            "recurring",
            "recurrence_rule",
            "reminder_settings",
            "user",
            "user_name",  # from another model
            "user_name_ar",  # from another model
        ]
        read_only_fields = ["event_id"]


class EventDialogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        field = ["event_id", "name"]
