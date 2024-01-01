from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

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

from apps.category.models import Category
from apps.category.filters import CategoryFilter
from apps.category.serializers import (
    CategorySerializer,
    NestedCategorySerializer,
    CategoryDeleteSerializer,
    CategoryImageSerializer,
    CategoryDialogSerializer,
    CategoryLevelDialogSerializer,
)


class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.action = self.request.method.lower()

    def perform_create(self, serializer):
        # lowercase the user's name before saving
        name = serializer.validated_data.get("name", "")
        capitalized_name = name.lower()
        serializer.save(
            name=capitalized_name,
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def create(self, request, *args, **kwargs):
        user = self.request.user
        allowed_roles = ["SUPERUSER", "OWNER", "MANAGER"]
        if user.role not in allowed_roles:
            raise PermissionDenied(_("You don't have permission to create categories."))

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {"detail": _("Category created successfully")},
            status=status.HTTP_201_CREATED,
        )

    def get_serializer_class(self):
        if self.action == "list":
            return CategorySerializer
        elif self.action == "upload_image":
            return CategoryImageSerializer
        return self.serializer_class

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        category = self.get_object()
        serializer = self.get_serializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ["name"]
    ordering_fields = ["name"]


class DeletedCategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ["name"]
    ordering_fields = ["name"]

    def get_queryset(self):
        user = self.request.user
        allowed_roles = ["SUPERUSER", "OWNER", "MANAGER"]
        if user.role not in allowed_roles:
            raise PermissionDenied(
                _("You don't have permission to view deleted categories.")
            )

        queryset = Category.objects.filter(is_deleted=True)
        return queryset


class CategoryRetrieveView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "category_id"  # Use 'slug' as the lookup field
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        category_id = self.request.query_params.get("category_id")
        category = get_object_or_404(Category, category_id=category_id)
        return category


class ChildrenCategoriesView(generics.ListAPIView):
    serializer_class = NestedCategorySerializer  # Use your Category serializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        slug = self.request.query_params.get("slug")
        parent_category = Category.objects.filter(slug=slug).first()

        if parent_category:
            return Category.objects.filter(parent=parent_category)
        else:
            return Category.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)


class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "category_id"
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        category_id = self.request.query_params.get("category_id")
        category = get_object_or_404(Category, category_id=category_id)
        return category

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"detail": _("Category updated successfully")}, status=status.HTTP_200_OK
        )


class CategoryDeleteTemporaryView(generics.RetrieveUpdateAPIView):
    serializer_class = CategoryDeleteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "category_id"

    def get_object(self):
        category_id = self.request.query_params.get("category_id")
        category = get_object_or_404(Category, category_id=category_id)
        return category

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        user = self.request.user
        allowed_roles = ["SUPERUSER", "OWNER", "MANAGER"]

        if user.role not in allowed_roles:
            raise PermissionDenied(_("You don't have permission to delete categories."))

        if instance.is_deleted:
            return Response(
                {"detail": _("Category is already deleted")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"detail": _("Category temp deleted successfully")},
            status=status.HTTP_200_OK,
        )


class CategoryRestoreView(generics.RetrieveUpdateAPIView):
    serializer_class = CategoryDeleteSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "category_id"

    def get_object(self):
        category_id = self.request.query_params.get("category_id")
        category = get_object_or_404(Category, category_id=category_id)
        return category

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        user = self.request.user
        allowed_roles = ["SUPERUSER", "OWNER", "MANAGER"]

        if user.role not in allowed_roles:
            raise PermissionDenied(
                _("You don't have permission to restore deleted categories.")
            )

        if instance.is_deleted == False:
            return Response(
                {"detail": _("Category is not deleted")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(
            {"detail": _("Category restored successfully")}, status=status.HTTP_200_OK
        )


class CategoryDeleteView(generics.DestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = "category_id"

    def get_object(self):
        category_id = self.request.query_params.get("category_id")
        category = get_object_or_404(Category, category_id=category_id)
        return category

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        category.delete()
        return Response(
            {"detail": _("Category permanently deleted successfully")},
            status=status.HTTP_204_NO_CONTENT,
        )


# dialog views
class CategoryDialogView(generics.ListAPIView):
    queryset = Category.objects.filter(is_deleted=False)
    serializer_class = CategoryDialogSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class ParentCategoryDialog(generics.ListAPIView):
    queryset = Category.objects.filter(parent__isnull=True, is_deleted=False)
    serializer_class = CategoryDialogSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class CategoryLevelDialogView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        role_choices = [
            {"value": 1, "display": _("Category")},
            {"value": 2, "display": _("Subcategory")},
            {"value": 3, "display": _("Sub-subcategory")},
        ]

        serializer = CategoryLevelDialogSerializer(role_choices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
