"""
Serializers for Notifications.
"""

from rest_framework import serializers

from .models import Notification, NotificationPreference, NotificationTemplate


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""

    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "template",
            "channel",
            "subject",
            "body",
            "status",
            "sent_at",
            "delivered_at",
            "error_message",
            "metadata",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates."""

    class Meta:
        model = NotificationTemplate
        fields = [
            "id",
            "name",
            "channel",
            "event_type",
            "subject",
            "body",
            "variables",
            "is_active",
        ]
        read_only_fields = ["id"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences."""

    class Meta:
        model = NotificationPreference
        fields = [
            "id",
            "email_enabled",
            "sms_enabled",
            "whatsapp_enabled",
            "push_enabled",
            "event_reminders",
            "approval_notifications",
            "payment_notifications",
            "marketing_emails",
        ]
        read_only_fields = ["id"]
