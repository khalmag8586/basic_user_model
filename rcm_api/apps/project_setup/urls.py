from django.urls import path

from apps.project_setup.views import(
    ProjectSetupCreateView,
    ProjectSetupListView,
    ProjectSetupUpdateView,
    ProjectSetupDeleteView,
    ThemeCreateView,
    ThemeListView,
    ThemeUpdateView,
    ThemeDeleteView,
)

app_name='project_setup'

urlpatterns = [
    path('setup_create/',ProjectSetupCreateView.as_view(),name='setup-create'),
    path('setup_list/',ProjectSetupListView.as_view(),name='setup-list'),
    path('setup_update/',ProjectSetupUpdateView.as_view(),name='setup-update'),
    path('setup_delete/',ProjectSetupDeleteView.as_view(),name='setup-delete'),
    #theme urls
    path('theme_create/',ThemeCreateView.as_view(),name='theme-create'),
    path('theme_list/',ThemeListView.as_view(),name='theme-list'),
    path('theme_update/',ThemeUpdateView.as_view(),name='theme-update'),
    path('theme_delete/',ThemeDeleteView.as_view(),name='theme-delete'),
]
