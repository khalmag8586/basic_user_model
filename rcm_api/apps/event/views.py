from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import (
    generics,
    status,
)
from rest_framework_simplejwt.authentication import JWTAuthentication

from rcm_api.pagination import StandardResultsSetPagination

from apps.event.models import Event
from apps.event.serializers import EventSerializer, EventDialogSerializer


class EventCreateView(generics.CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer

    def perform_create(self, serializer):
        # lowercase the user's name before saving
        name = serializer.validated_data.get("name", "")
        capitalized_name = name.lower()
        serializer.save(name=capitalized_name, user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {"detail": _("Event created successfully")},
            status=status.HTTP_201_CREATED,
        )


class EventListView(generics.ListAPIView):
    queryset = Event.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        "name",
        "start",
        "end",
    ]
    ordering_fields = ["name", "-name"]


class EventRetrieveView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer
    lookup_field = "event_id"

    def get_object(self):
        event_id = self.request.query_params.get("event_id")
        event = get_object_or_404(Event, event_id=event_id)
        return event


class EventUpdateView(generics.UpdateAPIView):
    queryset = Event.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = EventSerializer
    lookup_field = "event_id"

    def get_object(self):
        event_id = self.request.query_params.get("event_id")
        event = get_object_or_404(Event, event_id=event_id)
        return event

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"detail": _("Event updated successfully")}, status=status.HTTP_200_OK
        )


class EventDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "event_id"

    def get_object(self):
        event_id = self.request.query_params.get("event_id")
        event = get_object_or_404(Event, event_id=event_id)
        return event

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        category.delete()
        return Response(
            {"detail": _("Event permanently deleted successfully")},
            status=status.HTTP_204_NO_CONTENT,
        )
