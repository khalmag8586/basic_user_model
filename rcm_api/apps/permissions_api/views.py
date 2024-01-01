from django.contrib.auth.models import Permission, Group
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.permissions_api.serializers import (
    PermissionSerializer,
    GroupSerializer,
    PermissionDialogSerializer,
    GroupDialogSerializer,
)

from user.models import User
from user.serializers import UserSerializer


class PermissionListView(generics.ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class PermissionDialogView(generics.ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionDialogSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class AssignPermissionsToGroupView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        group_id = request.query_params.get("group_id")
        permission_codenames = request.data.get("codename", [])

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(
                {"error": _("Group not found")}, status=status.HTTP_404_NOT_FOUND
            )

        permissions = Permission.objects.filter(codename__in=permission_codenames)
        group.permissions.set(permissions)

        return Response(
            {"message": _("Permission(s) assigned to group successfully")},
            status=status.HTTP_201_CREATED,
        )


class AssignPermissionsToUserView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        permission_codenames = request.data.get("codename", [])

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": _("User not found")}, status=status.HTTP_404_NOT_FOUND
            )

        permissions = Permission.objects.filter(codename__in=permission_codenames)
        user.user_permissions.add(*permissions)

        return Response(
            {"message": _("Permission(s) assigned to user successfully")},
            status=status.HTTP_201_CREATED,
        )


class RemovePermissionsFromGroupView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        group_id = request.query_params.get("group_id")
        permission_codenames = request.data.get("codename", [])

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(
                {"error": _("Group not found")}, status=status.HTTP_404_NOT_FOUND
            )

        permissions = Permission.objects.filter(codename__in=permission_codenames)
        group.permissions.remove(*permissions)

        return Response(
            {"message": _("Permission(s) removed from group successfully")},
            status=status.HTTP_204_NO_CONTENT,
        )


class RemovePermissionsFromUserView(generics.UpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        permission_codenames = request.data.get("codename", [])

        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": _("Group not found")}, status=status.HTTP_404_NOT_FOUND
            )

        permissions = Permission.objects.filter(codename__in=permission_codenames)
        user.user_permissions.remove(*permissions)

        return Response(
            {"message": _("Permission(s) removed from user successfully")},
            status=status.HTTP_204_NO_CONTENT,
        )


# Groups Views
class GroupListView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class GroupCreateView(generics.CreateAPIView):
    serializer_class = GroupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": _("Group created successfully")}, status=status.HTTP_201_CREATED
        )


class GroupUpdateView(generics.UpdateAPIView):
    serializer_class = GroupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "group_id"

    def get_object(self):
        group_id = self.request.query_params.get("group_id")
        group = get_object_or_404(Group, id=group_id)
        return group

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"message": _("Group Updated successfully")}, status=status.HTTP_200_OK
        )


class GroupDeleteView(generics.DestroyAPIView):
    serializer_class = GroupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        group_id = self.request.query_params.get("group_id")
        group = get_object_or_404(Group, id=group_id)
        return group

    def delete(self, request, *args, **kwargs):
        group = self.get_object()  # Get the user instance
        group.delete()
        return Response(
            {"message": _("Group deleted successfully")},
            status=status.HTTP_204_NO_CONTENT,
        )


class GroupDialogView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupDialogSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class AssignUserToGroupView(generics.UpdateAPIView):
    serializer_class = UserSerializer  # Replace with your User serializer
    authentication_classes = [JWTAuthentication]  # Add your authentication classes
    permission_classes = [IsAuthenticated]  # Add your permission classes

    def update(self, request, *args, **kwargs):
        user_id = self.request.query_params.get("user_id")
        group_id = request.data.get("group_id")

        try:
            user = User.objects.get(user_id=user_id)
            group = Group.objects.get(id=group_id)
        except User.DoesNotExist:
            return Response(
                {"error": _("User not found")}, status=status.HTTP_404_NOT_FOUND
            )
        except Group.DoesNotExist:
            return Response(
                {"error": _("Group not found")}, status=status.HTTP_404_NOT_FOUND
            )

        user.groups.add(group)
        user.save()

        return Response(
            {"message": _("User assigned to group successfully")},
            status=status.HTTP_200_OK,
        )


class RemoveUserFromGroupView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()  # This queryset can be customized based on your needs
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user_id = self.request.query_params.get("user_id")
        group_id = request.data.get("group_id")

        try:
            user = User.objects.get(user_id=user_id)
            group = Group.objects.get(id=group_id)
        except User.DoesNotExist:
            return Response(
                {"error": _("User not found")}, status=status.HTTP_404_NOT_FOUND
            )
        except Group.DoesNotExist:
            return Response(
                {"error": _("Group not found")}, status=status.HTTP_404_NOT_FOUND
            )
        user.groups.remove(group)
        user.save()

        return Response(
            {"message": _("User removed from group successfully")},
            status=status.HTTP_204_NO_CONTENT,
        )
