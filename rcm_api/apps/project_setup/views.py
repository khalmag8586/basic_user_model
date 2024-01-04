from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import (
    generics,
    status,
)

from apps.project_setup.serializers import ProjectSetupSerializer, ThemeSerializer
from apps.project_setup.models import ProjectSetup, Theme


class ProjectSetupCreateView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSetupSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user
        if user.role != "SUPERUSER":
            raise PermissionDenied(
                _("You don't have permission to create project setup.")
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {"detail": _("Project setup created successfully")},
            status=status.HTTP_201_CREATED,
        )


class ProjectSetupListView(generics.ListAPIView):
    serializer_class = ProjectSetupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ProjectSetup.objects.all()

    def list(self, request, *args, **kwargs):
        user = self.request.user
        if user.role != "SUPERUSER":
            raise PermissionDenied(
                _("You don't have permission to view project setups.")
            )
        return super().list(request, *args, **kwargs)


class ProjectSetupUpdateView(generics.UpdateAPIView):
    serializer_class = ProjectSetupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        id = self.request.query_params.get("id")
        setup = get_object_or_404(ProjectSetup, id=id)
        return setup

    def update(self, request, *args, **kwargs):
        user = self.request.user
        if user.role != "SUPERUSER":
            raise PermissionDenied(
                _("You don't have permission to update project setups.")
            )
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"detail": _("Project setup updated successfully")},
            status=status.HTTP_200_OK,
        )


class ProjectSetupDeleteView(generics.DestroyAPIView):
    serializer_class = ProjectSetupSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        id = self.request.query_params.get("id")
        setup = get_object_or_404(ProjectSetup, id=id)
        return setup

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        if user.role != "SUPERUSER":
            raise PermissionDenied(
                _("You don't have permission to delete project setups.")
            )
        setup_obg = self.get_object()
        setup_obg.delete()
        return Response(
            {"detail": _("Project setup permanently deleted successfully")},
            status=status.HTTP_204_NO_CONTENT,
        )

#theme views
class ThemeCreateView(generics.CreateAPIView):
    serializer_class = ThemeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = self.request.user
        if user.role != "SUPERUSER":
            raise PermissionDenied(_("You don't have permission to create theme."))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {"detail": _("Theme setup created successfully")},
            status=status.HTTP_201_CREATED,
        )


class ThemeListView(generics.ListAPIView):
    serializer_class = ThemeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Theme.objects.all()

    def list(self, request, *args, **kwargs):
        user = self.request.user
        if user.role != "SUPERUSER":
            raise PermissionDenied(_("You don't have permission to view  themes."))
        return super().list(request, *args, **kwargs)


class ThemeUpdateView(generics.UpdateAPIView):
    serializer_class = ThemeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        id = self.request.query_params.get("id")
        theme = get_object_or_404(Theme, id=id)
        return theme

    def update(self, request, *args, **kwargs):
        user = self.request.user
        if user.role != "SUPERUSER":
            raise PermissionDenied(_("You don't have permission to update themes."))
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"detail": _("Theme updated successfully")},
            status=status.HTTP_200_OK,
        )


class ThemeDeleteView(generics.DestroyAPIView):
    serializer_class = ThemeSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        id = self.request.query_params.get("id")
        theme = get_object_or_404(Theme, id=id)
        return theme

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        if user.role != "SUPERUSER":
            raise PermissionDenied(_("You don't have permission to delete themes."))
        theme = self.get_object()
        theme.delete()
        return Response(
            {"detail": _("Theme permanently deleted successfully")},
            status=status.HTTP_204_NO_CONTENT,
        )
