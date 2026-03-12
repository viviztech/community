"""
Membership Models for ACTIV Membership Portal.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class MembershipTier(models.Model):
    """Membership tiers with pricing."""

    class TierType(models.TextChoices):
        LEARNER = "learner", _("Learner")
        BEGINNER = "beginner", _("Beginner")
        INTERMEDIATE = "intermediate", _("Intermediate")
        IDEAL = "ideal", _("Ideal")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    tier_type = models.CharField(max_length=20, choices=TierType.choices, unique=True)
    description = models.TextField()
    yearly_price = models.DecimalField(max_digits=10, decimal_places=2)
    lifetime_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = "membership_tiers"
        verbose_name = _("Membership Tier")
        verbose_name_plural = _("Membership Tiers")
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class Membership(models.Model):
    """Active membership for a member."""

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        EXPIRED = "expired", _("Expired")
        CANCELLED = "cancelled", _("Cancelled")
        PENDING = "pending", _("Pending Payment")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        "members.Member", on_delete=models.CASCADE, related_name="memberships"
    )
    tier = models.ForeignKey(
        MembershipTier, on_delete=models.PROTECT, related_name="memberships"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    membership_type = models.CharField(
        max_length=20, choices=[("yearly", "Yearly"), ("lifetime", "Lifetime")]
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    payment = models.OneToOneField(
        "payments.Payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="membership",
    )
    certificate_number = models.CharField(max_length=50, null=True, blank=True)
    certificate_issued_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "memberships"
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.member.user.full_name} - {self.tier.name}"

    def is_valid(self):
        """Check if membership is valid."""
        if self.membership_type == "lifetime":
            return self.status == "active"
        if self.end_date:
            return self.status == "active" and self.end_date >= timezone.now().date()
        return False

    def generate_certificate(self):
        """Generate membership certificate."""
        import uuid

        self.certificate_number = (
            f"ACTIV/{timezone.now().year}/{uuid.uuid4().hex[:6].upper()}"
        )
        self.certificate_issued_at = timezone.now()
        self.save()
        return self.certificate_number
