from django.urls import path
from apps.table.views import(
    TableCreateView,
    TableListView,
    TableRetrieveView,
    TableUpdateView,
    TableDeleteView,
)
app_name = "table"
urlpatterns = [
    path('table_create/',TableCreateView.as_view(),name='table-create'),
    path('table_list/',TableListView.as_view(),name='table-list'),
    path('table_retrieve/',TableRetrieveView.as_view(), name='table-retrieve'),
    path('table_update/',TableUpdateView.as_view(),name='table-update'),
    path('table_delete/',TableDeleteView.as_view(),name='table-delete'),
]
