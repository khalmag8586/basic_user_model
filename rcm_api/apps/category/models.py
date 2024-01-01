from django.db import models, IntegrityError
from django.db.models import Q, UniqueConstraint
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

import uuid
import os

from rest_framework.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _

from rcm_api.util import unique_slug_generator


def category_image_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"

    return os.path.join("uploads", "category", filename)


class Category(models.Model):
    CATEGORY_LEVEL_CHOICES = (
        (1, _("Category")),
        (2, _("Subcategory")),
        (3, _("Sub-subcategory")),
    )
    category_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, allow_unicode=True, unique=True)
    image = models.ImageField(blank=True, null=True, upload_to=category_image_file_path)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    level = models.PositiveIntegerField(choices=CATEGORY_LEVEL_CHOICES, default=1)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
                related_name="user_created_category",

        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="user_updated_category",
        blank=True,
        null=True,
    )

    def calculate_level(self):
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 1

    def save(self, *args, **kwargs):
        if self.parent:
            if self.parent.level >= 2:
                raise ValidationError(_("Subcategories cannot have subcategories."))
        self.calculate_level()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

@receiver(pre_save, sender=Category)
def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)
