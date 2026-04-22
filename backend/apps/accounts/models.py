"""
User and Authentication Models for ACTIV Membership Portal.
"""

import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    """Custom user manager for the User model."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user."""
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        # username must be unique — use email as username (truncated to 150 chars)
        extra_fields.setdefault("username", email[:150])
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for ACTIV Membership Portal.
    Uses email as the primary identifier instead of username.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    phone_number = PhoneNumberField(unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to="profiles/", null=True, blank=True)

    # Social Authentication Fields
    social_provider = models.CharField(max_length=50, null=True, blank=True)
    social_user_id = models.CharField(max_length=100, null=True, blank=True)

    # Verification
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_expiry = models.DateTimeField(null=True, blank=True)

    # Timestamps
    last_activity = models.DateTimeField(null=True, blank=True)

    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["social_provider", "social_user_id"]),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def generate_otp(self):
        """Generate a 6-digit OTP."""
        import random

        self.otp = "".join([str(random.randint(0, 9)) for _ in range(6)])
        self.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
        self.save(update_fields=["otp", "otp_expiry"])
        return self.otp

    def verify_otp(self, otp):
        """Verify the OTP."""
        if self.otp == otp and self.otp_expiry > timezone.now():
            self.otp = None
            self.otp_expiry = None
            self.phone_verified = True
            self.save(update_fields=["otp", "otp_expiry", "phone_verified"])
            return True
        return False

    def soft_delete(self):
        """Soft delete the user."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save(update_fields=["is_deleted", "deleted_at", "is_active"])


class AdminProfile(models.Model):
    """
    Explicit role record for Block / District / State / Super admins.
    A user can hold at most one admin role at a time.
    Nominated by a higher-level admin and activated once approved.
    """

    class AdminLevel(models.TextChoices):
        BLOCK = "block", _("Block Admin")
        DISTRICT = "district", _("District Admin")
        STATE = "state", _("State Admin")
        SUPER = "super", _("Super Admin")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending Approval")
        ACTIVE = "active", _("Active")
        REVOKED = "revoked", _("Revoked")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="admin_profile",
    )
    admin_level = models.CharField(max_length=10, choices=AdminLevel.choices)
    area = models.ForeignKey(
        "members.GeographicArea",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="admins",
        help_text="The geographic area this admin is responsible for (null for Super Admin)",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    nominated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nominations_made",
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nominations_approved",
    )
    nomination_notes = models.TextField(blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoke_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "admin_profiles"
        verbose_name = _("Admin Profile")
        verbose_name_plural = _("Admin Profiles")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} — {self.get_admin_level_display()} ({self.get_status_display()})"

    def activate(self, approved_by_user):
        self.status = self.Status.ACTIVE
        self.approved_by = approved_by_user
        self.activated_at = timezone.now()
        self.save(update_fields=["status", "approved_by", "activated_at", "updated_at"])

    def revoke(self, reason=""):
        self.status = self.Status.REVOKED
        self.revoked_at = timezone.now()
        self.revoke_reason = reason
        self.save(update_fields=["status", "revoked_at", "revoke_reason", "updated_at"])
