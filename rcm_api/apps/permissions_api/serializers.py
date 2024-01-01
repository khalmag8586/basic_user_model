from rest_framework import serializers
from django.contrib.auth.models import Permission, Group


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


# Dialogs Serializers
class PermissionDialogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["codename", "name",'content_type']
        # fields = ["name",]

class GroupDialogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["id", "name"]
