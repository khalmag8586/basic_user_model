from django.db import models, IntegrityError
from django.db.models import Q, UniqueConstraint
from django.conf import settings
from django.core.files.base import ContentFile

import uuid
import os
from PIL import Image
from io import BytesIO



from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


def default_photo_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f"default{ext}"
    return os.path.join("default_photos", filename)


def user_photo_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    return os.path.join("uploads", "employee", filename)


class UserManager(BaseUserManager):
    def create_user(
        self, email=None, mobile_number=None, password=None, **extra_fields
    ):
        if not email and not mobile_number:
            raise ValueError(
                _("User must have either an email address or a mobile number")
            )

        user = self.model(
            email=self.normalize_email(email),
            mobile_number=mobile_number,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, mobile_number=None, password=None):
        if not email and not mobile_number:
            raise ValueError(
                _("Superuser must have either an email address or a mobile number")
            )

        user = self.create_user(
            email=email,
            mobile_number="01112890867",
            password=password,
            role=User.Role.SUPERUSER,  # Set the role to SUPERUSER for superuser
            name="KhalMag",
            name_ar="كالماج",  # Set the desired name for superuser
        )

        user.is_staff = True
        user.is_superuser = True
        user.photo = "default_photos/km2.jpg"

        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        SUPERUSER = "SUPERUSER", _("SuperUser")
        OWNER = "OWNER", _("Owner")
        MANAGER = "MANAGER", _("Manager")
        WAITER = "WAITER", _("waiter")
        CASHIER = "CASHIER", _("Cashier")
        CHEF = "CHEF", _("Chef")
        DELIVERY = "DELIVERY", _("Delivery")

    GENDER_CHOICES = [("male", _("Male")), ("female", _("Female"))]

    mobile_num_regex = RegexValidator(
        regex="^[0-9]{10,11}$",
        message=_("Entered mobile number isn't in a right format!"),
    )
    id_regex = RegexValidator(
        regex="^[0-9]{15}$", message=_("Entered ID number isn't in a right format!")
    )
    # user personal info
    user_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        primary_key=True,
    )
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    nationality = models.CharField(max_length=255, blank=True, null=True)
    passport = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    identification = models.CharField(validators=[id_regex], max_length=15, unique=True)
    birthdate = models.DateField(blank=True, null=True)
    role = models.CharField(max_length=50, choices=Role.choices)
    position = models.CharField(max_length=255)
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        default="male",
        blank=True,
        null=True,
    )

    education = models.CharField(max_length=255, blank=True, null=True)
    home_address = models.TextField(blank=True, null=True)
    mobile_number = models.CharField(
        validators=[mobile_num_regex],
        unique=True,
        max_length=11,
    )

    photo = models.ImageField(
        blank=True,
        null=True,
        upload_to=user_photo_file_path,
    )
    avatar = models.ImageField(blank=True, null=True, upload_to=user_photo_file_path)
    cover = models.ImageField(blank=True, null=True, upload_to=user_photo_file_path)

    # user's bank info
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_branch = models.CharField(max_length=255, blank=True, null=True)
    bank_account_name = models.CharField(max_length=255, blank=True, null=True)
    bank_account_number = models.CharField(max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Resize and save the avatar image
        if self.photo and not self.avatar:
            self.resize_and_save_avatar()

    def resize_and_save_avatar(self):
        # Check if the photo field is not empty
        if self.photo:
            photo_path = self.photo.path

            # Check if the avatar field is not already set
            if not self.avatar:
                # Open the image using Pillow
                with Image.open(photo_path) as img:
                    # Resize the image (adjust the size as needed)
                    resized_img = img.resize((300, 300))

                    # Save the resized image as the avatar
                    buffer = BytesIO()
                    resized_img.save(buffer, format="PNG")
                    self.avatar.save("avatar.png", ContentFile(buffer.getvalue()), save=True)

    class Meta:
        def __str__(self):
            return self.email

