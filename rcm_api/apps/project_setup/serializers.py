from rest_framework import serializers

from apps.project_setup.models import ProjectSetup, Theme


class ProjectSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSetup
        fields = [
            "id",
            "project_name",
            "color_list",
            "lang",
            "logo",
            "login_photo",
            "domain_name",
            "owner_email",
            "owner_name",
            "business_type",
            "country",
            "currency_ar",
            "currency_en",
            "front_data",
        ]
        read_only_fields = ["id"]

#theme
class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = [
            "id",
            "name",
            "primary",
            "secondary",
            "error",
            "background",
            "surface",
            "info",
            "success",
            "warning",
            "dark",
        ]
        read_only_fields = ["id"]
