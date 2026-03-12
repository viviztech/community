"""
Event Models for ACTIV Membership Portal.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Event(models.Model):
    """Event model for ACTIV events."""

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")
        CANCELLED = "cancelled", _("Cancelled")
        COMPLETED = "completed", _("Completed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    venue = models.CharField(max_length=255)
    event_date = models.DateTimeField()
    registration_deadline = models.DateTimeField(null=True, blank=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_delegates = models.IntegerField(default=1)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    image = models.ImageField(upload_to="events/", null=True, blank=True)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="organized_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "events"
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ["-event_date"]

    def __str__(self):
        return self.title

    @property
    def is_upcoming(self):
        return self.event_date > timezone.now()

    @property
    def available_tickets(self):
        booked = (
            self.registrations.filter(payment_status="completed").aggregate(
                total=models.Sum("number_of_delegates")
            )["total"]
            or 0
        )
        return max(0, self.max_delegates - booked)


class EventRegistration(models.Model):
    """Event registration with delegate details."""

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        COMPLETED = "completed", _("Completed")
        REFUNDED = "refunded", _("Refunded")
        FAILED = "failed", _("Failed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="registrations"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.CASCADE, related_name="event_registrations"
    )
    number_of_delegates = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    payment = models.OneToOneField(
        "payments.Payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event_registration",
    )
    qr_code = models.CharField(max_length=100, null=True, blank=True)
    ticket_number = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "event_registrations"
        verbose_name = _("Event Registration")
        verbose_name_plural = _("Event Registrations")

    def __str__(self):
        return f"{self.member.user.full_name} - {self.event.title}"

    def generate_ticket(self):
        """Generate ticket number and QR code."""
        import uuid

        self.ticket_number = (
            f"TKT/{self.event.id.hex[:8].upper()}/{uuid.uuid4().hex[:6].upper()}"
        )
        self.qr_code = str(uuid.uuid4())
        self.save()
        return self.ticket_number


class Delegate(models.Model):
    """Delegate details for event registration."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration = models.ForeignKey(
        EventRegistration, on_delete=models.CASCADE, related_name="delegates"
    )
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    designation = models.CharField(max_length=100, null=True, blank=True)
    organization = models.CharField(max_length=255, null=True, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "delegates"
        verbose_name = _("Delegate")
        verbose_name_plural = _("Delegates")

    def __str__(self):
        return self.name
