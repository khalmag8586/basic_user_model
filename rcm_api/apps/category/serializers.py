from rest_framework import serializers

from apps.category.models import Category


class ParentCategoryNameField(serializers.SlugRelatedField):
    queryset = Category.objects.all()
    slug_field = "name"


class CategorySerializer(serializers.ModelSerializer):
    parent = ParentCategoryNameField(
        queryset=Category.objects.all(),
        slug_field="name",
        allow_null=True,
        required=False,
    )
    created_by_user_name = serializers.CharField(source='created_by.name',read_only=True)
    created_by_user_name_ar = serializers.CharField(source="created_by.name_ar", read_only=True)
    updated_by_user_name = serializers.CharField(source="updated_by.name", read_only=True)
    updated_by_user_name_ar = serializers.CharField(source="updated_by.name_ar", read_only=True)
    class Meta:
        model = Category
        fields = [
            "category_id",
            "name",
            "description",
            "parent",
            "slug",
            "level",
            "created_at",
            "updated_at",
            "image",
            "is_active",
            "created_by",
            "created_by_user_name",  # from another model
            "created_by_user_name_ar",  # from another model
            "updated_by",
            "updated_by_user_name", # from another model
            "updated_by_user_name_ar", # from another model
        ]
        read_only_fields = [
            "category_id",
            "slug",
            "level",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]


class NestedCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("category_id", "name", "slug", "children")

    def get_children(self, obj):
        children = Category.objects.filter(parent=obj)
        serializer = NestedCategorySerializer(children, many=True)
        return serializer.data


class CategoryDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["is_deleted"]


class CategoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "image"]
        read_only_fields = ["category_id"]
        extra_kwargs = {"image": {"required": "True"}}


class CategoryDialogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["category_id", "name", "slug"]

class CategoryLevelDialogSerializer(serializers.Serializer):
    value = serializers.CharField()
    display = serializers.CharField()
