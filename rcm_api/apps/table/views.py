from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import (
    generics,
    status,
)
from rest_framework_simplejwt.authentication import JWTAuthentication

from rcm_api.pagination import StandardResultsSetPagination

from apps.table.serializers import TableSerializer, TableDialogSerializer
from apps.table.models import RCTable


class TableCreateView(generics.CreateAPIView):
    serializer_class = TableSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        allowed_roles = ["SUPERUSER", "OWNER", "MANAGER"]
        if user.role not in allowed_roles:
            raise PermissionDenied(_("You don't have permission to create tables."))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {"detail": _("Table created successfully")},
            status=status.HTTP_201_CREATED,
        )


class TableListView(generics.ListAPIView):
    serializer_class = TableSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RCTable.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["table_number", "capacity", "chairs"]
    ordering_fields = ["table_number", "-table_number"]


class TableRetrieveView(generics.RetrieveAPIView):
    serializer_class = TableSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "table_id"

    def get_object(self):
        table_id = self.request.query_params.get("table_id")
        table = get_object_or_404(RCTable, table_id=table_id)
        return table


class TableUpdateView(generics.UpdateAPIView):
    serializer_class = TableSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "table_id"

    def get_object(self):
        table_id = self.request.query_params.get("table_id")
        table = get_object_or_404(RCTable, table_id=table_id)
        return table

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"detail": _("Table updated successfully")}, status=status.HTTP_200_OK
        )


class TableDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "table_id"

    def get_object(self):
        table_id = self.request.query_params.get("table_id")
        table = get_object_or_404(RCTable, table_id=table_id)
        return table

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        category.delete()
        return Response(
            {"detail": _("Table permanently deleted successfully")},
            status=status.HTTP_204_NO_CONTENT,
        )
