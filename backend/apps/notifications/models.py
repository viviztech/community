"""
Models for Notifications.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationTemplate(models.Model):
    """Email/SMS/WhatsApp notification templates."""

    class Channel(models.TextChoices):
        EMAIL = "email", _("Email")
        SMS = "sms", _("SMS")
        WHATSAPP = "whatsapp", _("WhatsApp")

    class EventType(models.TextChoices):
        REGISTRATION = "registration", _("Registration")
        APPROVAL = "approval", _("Approval")
        REJECTION = "rejection", _("Rejection")
        PAYMENT = "payment", _("Payment")
        EVENT_REMINDER = "event_reminder", _("Event Reminder")
        MEMBERSHIP_EXPIRY = "membership_expiry", _("Membership Expiry")
        GENERAL = "general", _("General")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    channel = models.CharField(max_length=20, choices=Channel.choices)
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    subject = models.CharField(max_length=200, null=True, blank=True)
    body = models.TextField()
    variables = models.JSONField(default=list)  # List of template variables
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_templates"
        verbose_name = _("Notification Template")
        verbose_name_plural = _("Notification Templates")

    def __str__(self):
        return f"{self.name} ({self.get_channel_display()})"


class Notification(models.Model):
    """Individual notifications sent to users."""

    class Channel(models.TextChoices):
        EMAIL = "email", _("Email")
        SMS = "sms", _("SMS")
        WHATSAPP = "whatsapp", _("WhatsApp")
        PUSH = "push", _("Push Notification")
        IN_APP = "in_app", _("In-App")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SENT = "sent", _("Sent")
        DELIVERED = "delivered", _("Delivered")
        FAILED = "failed", _("Failed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        related_name="notifications",
    )
    channel = models.CharField(max_length=20, choices=Channel.choices)
    subject = models.CharField(max_length=200, null=True, blank=True)
    body = models.TextField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification to {self.user.email} - {self.get_status_display()}"


class NotificationPreference(models.Model):
    """User notification preferences."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preference",
    )
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    whatsapp_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    event_reminders = models.BooleanField(default=True)
    approval_notifications = models.BooleanField(default=True)
    payment_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)

    class Meta:
        db_table = "notification_preferences"
        verbose_name = _("Notification Preference")
        verbose_name_plural = _("Notification Preferences")

    def __str__(self):
        return f"Preferences for {self.user.email}"
