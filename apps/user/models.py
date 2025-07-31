from typing import ClassVar

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    PermissionsMixin,
)
from django.db import models

class UserRoles:
    ADMIN = "admin"
    VALUE_CHAIN_PARTNER = "value-chain-partner"
    ASSESSMENT_AGENCY = "assessment-agency"
    VP_COMPLIANCE = "vp-compliance"
    EMPANELMENT_REVIEWER = "empanelment-reviewer"

    CHOICES = [
        ADMIN,
        VALUE_CHAIN_PARTNER,
        ASSESSMENT_AGENCY,
        VP_COMPLIANCE,
        EMPANELMENT_REVIEWER,
    ]


class CustomUserManager(SoftDeleteManager, BaseUserManager):
    def make_random_password(self, *args, **kwargs):
        return super().make_random_password(*args, **kwargs)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required.")
        if not extra_fields.get("organization"):
            raise ValueError("The Organization field is required.")
        if not extra_fields.get("full_name"):
            raise ValueError("The Full name is required.")
        if not extra_fields.get("phone"):
            raise ValueError("The Phone is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        # Ensure required fields for superuser creation:
        if not extra_fields.get("organization"):
            raise ValueError("Superuser must have an organization.")
        if not extra_fields.get("full_name"):
            raise ValueError("Superuser must have full_name.")
        if not extra_fields.get("phone"):
            raise ValueError("Superuser must have phone.")

        if extra_fields.get("organization"):
            org_id = extra_fields.get("organization")
            org = Organization.objects.get(id=org_id)
            extra_fields["organization"] = org

        return self.create_user(email, password, **extra_fields)


def upload_avatar_path(instance, filename):
    return f"avatar/{filename}"


class CustomUser(AbstractBaseUser, PermissionsMixin, TimestampMixin, SoftDeleteMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, related_name="users"
    )

    frappe_lms_user_created_on = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "organization", "phone"]

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

    def make_value_chain_partner(self, clear_existing: bool = False):
        self.assign_role(UserRoles.VALUE_CHAIN_PARTNER, clear_existing)

    def make_assessment_agency(self, clear_existing: bool = False):
        self.assign_role(UserRoles.ASSESSMENT_AGENCY, clear_existing)

    def make_vp_compliance(self, clear_existing: bool = False):
        self.assign_role(UserRoles.VP_COMPLIANCE, clear_existing)

    def make_empanelment_reviewer(self, clear_existing: bool = False):
        self.assign_role(UserRoles.EMPANELMENT_REVIEWER, clear_existing)

    def has_role(self, role_name: str) -> bool:
        """Check if user is in a given role group."""
        return self.groups.filter(name=role_name).exists()

    def is_admin(self):
        return self.has_role(UserRoles.ADMIN)

    def is_value_chain_partner(self):
        return self.has_role(UserRoles.VALUE_CHAIN_PARTNER)

    def is_assessment_agency(self):
        return self.has_role(UserRoles.ASSESSMENT_AGENCY)

    def is_vp_compliance(self):
        return self.has_role(UserRoles.VP_COMPLIANCE)

    def is_empanelment_reviewer(self):
        return self.has_role(UserRoles.EMPANELMENT_REVIEWER)
