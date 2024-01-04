from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]
urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path('api/project_setup/',include('apps.project_setup.urls')),
    path("api/users/", include("user.urls")),
    path("api/permissions/", include("apps.permissions_api.urls")),
    path("api/category/", include("apps.category.urls")),
    path("api/event/", include("apps.event.urls")),
    path("api/table/", include("apps.table.urls")),

)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
