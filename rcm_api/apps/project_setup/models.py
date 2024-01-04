from django.db import models
import os
import uuid
from django.contrib.postgres.fields import ArrayField


def logo_photo_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    return os.path.join("project_photo", "logo", filename)


def login_photo_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    return os.path.join("project_photo", "login", filename)


class ProjectSetup(models.Model):
    project_name = models.CharField(max_length=255, null=True, blank=True)
    main_color = models.CharField(max_length=255, null=True, blank=True)
    secondary_color = models.CharField(max_length=255, null=True, blank=True)
    color_list = ArrayField(models.CharField(max_length=255, null=True, blank=True))
    lang = models.CharField(max_length=255)
    logo = models.ImageField(
        blank=True,
        null=True,
        upload_to=logo_photo_file_path,
    )
    login_photo = models.ImageField(
        blank=True,
        null=True,
        upload_to=login_photo_file_path,
    )
    domain_name = models.CharField(max_length=255, null=True, blank=True)
    owner_email = models.CharField(max_length=255, null=True, blank=True)
    owner_name = models.CharField(max_length=255, null=True, blank=True)
    business_type = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    currency_ar = models.CharField(max_length=255, null=True, blank=True)
    currency_en = models.CharField(max_length=255, null=True, blank=True)
    front_data = models.JSONField(null=True, blank=True)


class Theme(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    primary = models.CharField(max_length=255, null=True, blank=True)
    secondary = models.CharField(max_length=255, null=True, blank=True)
    error = models.CharField(max_length=255, null=True, blank=True)
    background = models.CharField(max_length=255, null=True, blank=True)
    surface = models.CharField(max_length=255, null=True, blank=True)
    info = models.CharField(max_length=255, null=True, blank=True)
    success = models.CharField(max_length=255, null=True, blank=True)
    warning = models.CharField(max_length=255, null=True, blank=True)
    dark = models.BooleanField(default=False)
