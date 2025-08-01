from typing import ClassVar

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    PermissionsMixin,
)
from django.db import models

from apps.common.models import SoftDeleteManager, SoftDeleteMixin, TimestampMixin


class UserRoles:
    ADMIN = "admin"

    CHOICES = [
        ADMIN,
    ]


class CustomUserManager(SoftDeleteManager, BaseUserManager):
    def make_random_password(self, *args, **kwargs):
        return super().make_random_password(*args, **kwargs)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required.")
        if not extra_fields.get("full_name"):
            raise ValueError("The Full name is required.")
        if not extra_fields.get("phone"):
            raise ValueError("The Phone is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin, TimestampMixin, SoftDeleteMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "phone"]

    objects: ClassVar[CustomUserManager] = CustomUserManager()

    def __str__(self):
        return self.email

    def assign_role(self, role_name: str, clear_existing: bool = False):
        """Assign this user to a Django group."""

        if role_name not in UserRoles.CHOICES:
            raise ValueError(f"Invalid role: {role_name}")

        if clear_existing:
            self.groups.clear()

        try:
            group = Group.objects.get(name=role_name)
        except Group.DoesNotExist:
            raise ValueError(f"Group with name {role_name} not found")

        self.groups.add(group)

    def make_admin(self, clear_existing: bool = False):
        self.assign_role(UserRoles.ADMIN, clear_existing)

    def has_role(self, role_name: str) -> bool:
        """Check if user is in a given role group."""
        return self.groups.filter(name=role_name).exists()

    def is_admin(self):
        return self.has_role(UserRoles.ADMIN)
