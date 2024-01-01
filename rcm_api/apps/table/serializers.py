from rest_framework import serializers

from apps.table.models import RCTable


class TableSerializer(serializers.ModelSerializer):
    created_by_user_name = serializers.CharField(
        source="created_by.name", read_only=True
    )
    created_by_user_name_ar = serializers.CharField(
        source="created_by.name_ar", read_only=True
    )
    updated_by_user_name = serializers.CharField(
        source="updated_by.name", read_only=True
    )
    updated_by_user_name = serializers.CharField(
        source="updated_by.name_ar", read_only=True
    )

    class Meta:
        model = RCTable
        fields = [
            "table_id",
            "table_number",
            "capacity",
            "chairs",
            "description",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_user_name",
            "created_by_user_name_ar",
            "updated_by",
            "updated_by_user_name",
            "updated_by_user_name",
            "is_available",
            "is_reserved",
        ]
        read_only_fields = [
            "table_id",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

class TableDialogSerializer(serializers.Serializer):
    value = serializers.CharField()
    display = serializers.CharField()