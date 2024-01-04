from django.urls import path
from apps.event.views import (
    EventCreateView,
    EventListView,
    EventRetrieveView,
    EventUpdateView,
    EventDeleteView,
    EventDialogView,
)

app_name = "event"

urlpatterns = [
    path("event_create/", EventCreateView.as_view(), name="event-create"),
    path("event_list/", EventListView.as_view(), name="event-list"),
    path("event_retrieve/", EventRetrieveView.as_view(), name="event-retrieve"),
    path("event_update/", EventUpdateView.as_view(), name="event-update"),
    path("event_delete/", EventDeleteView.as_view(), name="event-delete"),
    path("event_dialog/", EventDialogView.as_view(), name="event-dialog"),
]
