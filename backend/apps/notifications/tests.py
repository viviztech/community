"""
Tests for Notifications app.
"""

from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from .views import NotificationListView, NotificationSendView


@pytest.mark.django_db
class TestNotificationViews:
    """Tests for Notification views."""

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = APIRequestFactory()

    @patch("apps.notifications.views.send_sms_notification")
    def test_send_sms_notification(self, mock_send_sms):
        """Test sending SMS notification."""
        mock_send_sms.return_value = True

        from .views import NotificationSendView

        view = NotificationSendView.as_view()

        request = self.factory.post(
            "/api/v1/notifications/send/",
            {"phone": "+919876543210", "message": "Test SMS"},
            format="json",
        )

        response = view(request)
        assert response.status_code == 200
        mock_send_sms.assert_called_once()

    @patch("apps.notifications.views.send_whatsapp_notification")
    def test_send_whatsapp_notification(self, mock_send_whatsapp):
        """Test sending WhatsApp notification."""
        mock_send_whatsapp.return_value = True

        from .views import NotificationSendView

        view = NotificationSendView.as_view()

        request = self.factory.post(
            "/api/v1/notifications/send/",
            {
                "phone": "+919876543210",
                "message": "Test WhatsApp",
                "channel": "whatsapp",
            },
            format="json",
        )

        response = view(request)
        assert response.status_code == 200
        mock_send_whatsapp.assert_called_once()


@pytest.mark.django_db
class TestNotificationModels:
    """Tests for Notification models."""

    def test_notification_creation(self):
        """Test creating a notification."""
        from .models import Notification

        notification = Notification.objects.create(
            title="Test Notification",
            message="This is a test message",
            notification_type="sms",
        )

        assert notification.title == "Test Notification"
        assert notification.status == "pending"
        assert str(notification) == "Test Notification"
