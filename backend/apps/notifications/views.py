"""
Views for Notifications.
"""

import json

import requests
from django.conf import settings
from django.template import Context, Template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DeviceToken, Notification, NotificationPreference, NotificationTemplate
from .serializers import (
    DeviceTokenSerializer,
    NotificationPreferenceSerializer,
    NotificationSerializer,
    NotificationTemplateSerializer,
)


class FCMService:
    """Service for sending Firebase Cloud Messaging push notifications."""

    @staticmethod
    def send_push(user, title, body, data=None):
        """Send push notification to all active device tokens for a user."""
        try:
            server_key = settings.FCM_SERVER_KEY
            if not server_key:
                return False

            tokens = list(
                DeviceToken.objects.filter(user=user, is_active=True).values_list("token", flat=True)
            )
            if not tokens:
                return False

            payload = {
                "registration_ids": tokens,
                "notification": {"title": title, "body": body},
                "data": data or {},
            }

            response = requests.post(
                "https://fcm.googleapis.com/fcm/send",
                headers={
                    "Authorization": f"key={server_key}",
                    "Content-Type": "application/json",
                },
                data=json.dumps(payload),
                timeout=30,
            )

            result = response.json()
            # Deactivate tokens that are no longer registered
            if result.get("failure", 0) > 0:
                for idx, res in enumerate(result.get("results", [])):
                    if res.get("error") in ("NotRegistered", "InvalidRegistration"):
                        DeviceToken.objects.filter(token=tokens[idx]).update(is_active=False)

            Notification.objects.create(
                user=user,
                channel=Notification.Channel.PUSH,
                subject=title,
                body=body,
                status=Notification.Status.SENT,
                sent_at=timezone.now(),
            )
            return True
        except Exception as e:
            print(f"FCM push error: {e}")
            return False


class TwilioService:
    """Service for sending SMS via Twilio."""

    @staticmethod
    def send_sms(to, message):
        """Send SMS using Twilio."""
        try:
            account_sid = settings.TWILIO_ACCOUNT_SID
            auth_token = settings.TWILIO_AUTH_TOKEN
            from_number = settings.TWILIO_PHONE_NUMBER

            if not all([account_sid, auth_token, from_number]):
                print("Twilio credentials not configured")
                return False

            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

            auth = (account_sid, auth_token)
            data = {
                "To": to,
                "From": from_number,
                "Body": message,
            }

            response = requests.post(url, auth=auth, data=data, timeout=30)

            if response.status_code == 201:
                result = response.json()
                return {
                    "success": True,
                    "message_sid": result.get("sid"),
                    "status": result.get("status"),
                }
            else:
                print(f"Twilio error: {response.text}")
                return {"success": False, "error": response.text}
        except Exception as e:
            print(f"Twilio SMS error: {e}")
            return {"success": False, "error": str(e)}


class WhatsAppService:
    """Service for sending WhatsApp messages via WhatsApp Business API."""

    @staticmethod
    def send_message(to, message):
        """Send WhatsApp message using WhatsApp Business API."""
        try:
            business_id = settings.WHATSAPP_BUSINESS_ID
            phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
            access_token = settings.WHATSAPP_ACCESS_TOKEN

            if not all([business_id, phone_number_id, access_token]):
                print("WhatsApp credentials not configured")
                return False

            # Format phone number for WhatsApp (use wa_id format)
            wa_id = to.replace("+", "").replace(" ", "")

            url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            data = {
                "messaging_product": "whatsapp",
                "to": wa_id,
                "type": "text",
                "text": {"body": message},
            }

            response = requests.post(
                url, headers=headers, data=json.dumps(data), timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                }
            else:
                print(f"WhatsApp error: {response.text}")
                return {"success": False, "error": response.text}
        except Exception as e:
            print(f"WhatsApp error: {e}")
            return {"success": False, "error": str(e)}


class NotificationService:
    """Service class for sending notifications."""

    @staticmethod
    def send_email(user, subject, body, html_body=None, attachments=None):
        """Send email notification. attachments: list of (filename, bytes, mimetype)."""
        from django.core.mail import EmailMessage

        try:
            email = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            if html_body:
                email.content_subtype = "html"
                email.body = html_body

            for filename, content, mimetype in (attachments or []):
                email.attach(filename, content, mimetype)

            email.send(fail_silently=False)

            # Create notification record
            Notification.objects.create(
                user=user,
                channel=Notification.Channel.EMAIL,
                subject=subject,
                body=body,
                status=Notification.Status.SENT,
                sent_at=timezone.now(),
            )

            return True
        except Exception as e:
            print(f"Email send error: {e}")
            return False

    @staticmethod
    def send_sms(user, message):
        """Send SMS notification."""
        try:
            if not user.phone_number:
                return False

            phone_str = str(user.phone_number)

            # Send via Twilio
            result = TwilioService.send_sms(phone_str, message)

            if result and result.get("success"):
                Notification.objects.create(
                    user=user,
                    channel=Notification.Channel.SMS,
                    body=message,
                    status=Notification.Status.SENT,
                    sent_at=timezone.now(),
                    metadata={"message_sid": result.get("message_sid")},
                )
                return True
            else:
                # Create failed notification record
                Notification.objects.create(
                    user=user,
                    channel=Notification.Channel.SMS,
                    body=message,
                    status=Notification.Status.FAILED,
                    error_message=result.get("error") if result else "Unknown error",
                )
                return False
        except Exception as e:
            print(f"SMS send error: {e}")
            return False

    @staticmethod
    def send_whatsapp(user, message):
        """Send WhatsApp notification."""
        try:
            if not user.phone_number:
                return False

            phone_str = str(user.phone_number)

            # Send via WhatsApp Business API
            result = WhatsAppService.send_message(phone_str, message)

            if result and result.get("success"):
                Notification.objects.create(
                    user=user,
                    channel=Notification.Channel.WHATSAPP,
                    body=message,
                    status=Notification.Status.SENT,
                    sent_at=timezone.now(),
                    metadata={"message_id": result.get("message_id")},
                )
                return True
            else:
                Notification.objects.create(
                    user=user,
                    channel=Notification.Channel.WHATSAPP,
                    body=message,
                    status=Notification.Status.FAILED,
                    error_message=result.get("error") if result else "Unknown error",
                )
                return False
        except Exception as e:
            print(f"WhatsApp send error: {e}")
            return False

    @staticmethod
    def send_notification(user, event_type, context, channels=None):
        """Send notification through specified channels using templates."""
        if channels is None:
            channels = ["email"]

        try:
            template = NotificationTemplate.objects.get(
                event_type=event_type, is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            print(f"Template not found for event_type: {event_type}")
            return False

        results = {}

        for channel in channels:
            if channel == "email" and template.channel in [
                "email",
                NotificationTemplate.Channel.EMAIL,
            ]:
                subject = NotificationService.render_template(template.subject, context)
                body = NotificationService.render_template(template.body, context)
                results["email"] = NotificationService.send_email(user, subject, body)

            elif channel == "sms" and template.channel in [
                "sms",
                NotificationTemplate.Channel.SMS,
            ]:
                body = NotificationService.render_template(template.body, context)
                results["sms"] = NotificationService.send_sms(user, body)

            elif channel == "whatsapp" and template.channel in [
                "whatsapp",
                NotificationTemplate.Channel.WHATSAPP,
            ]:
                body = NotificationService.render_template(template.body, context)
                results["whatsapp"] = NotificationService.send_whatsapp(user, body)

        return results

    @staticmethod
    def send_push(user, title, body, data=None):
        """Send push notification via FCM."""
        return FCMService.send_push(user, title, body, data)

    @staticmethod
    def render_template(template_str, context):
        """Render template with context variables."""
        if not template_str:
            return ""
        template = Template(template_str)
        context = Context(context)
        return template.render(context)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for notification templates."""

    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for notifications."""

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    @action(detail=False, methods=["get"])
    def unread(self, request):
        """Get unread notifications."""
        notifications = self.get_queryset().filter(status=Notification.Status.SENT)[:20]
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        self.get_queryset().update(status=Notification.Status.DELIVERED)
        return Response({"status": "success"})

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.status = Notification.Status.DELIVERED
        notification.save()
        return Response({"status": "success"})


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet for notification preferences."""

    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create notification preferences for user."""
        if hasattr(request.user, "notification_preference"):
            return Response(
                {"error": "Preferences already exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        preference = NotificationPreference.objects.create(
            user=request.user, **request.data
        )
        return Response(
            NotificationPreferenceSerializer(preference).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"])
    def my_preferences(self, request):
        """Get current user's notification preferences."""
        try:
            preference = NotificationPreference.objects.get(user=request.user)
            return Response(NotificationPreferenceSerializer(preference).data)
        except NotificationPreference.DoesNotExist:
            return Response(
                {
                    "email_enabled": True,
                    "sms_enabled": True,
                    "whatsapp_enabled": True,
                    "push_enabled": True,
                }
            )


class SendNotificationView(APIView):
    """API view to send custom notifications."""

    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        """Send notification to a user."""
        user_id = request.data.get("user_id")
        channel = request.data.get("channel", "email")
        subject = request.data.get("subject", "")
        body = request.data.get("body", "")

        try:
            from apps.accounts.models import User

            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if channel == "email":
            success = NotificationService.send_email(user, subject, body)
        elif channel == "sms":
            success = NotificationService.send_sms(user, body)
        elif channel == "whatsapp":
            success = NotificationService.send_whatsapp(user, body)
        else:
            return Response(
                {"error": "Invalid channel"}, status=status.HTTP_400_BAD_REQUEST
            )

        if success:
            return Response({"status": "sent"})
        return Response(
            {"error": "Failed to send notification"},
            status=status.HTTP_500_SERVER_ERROR,
        )


class DeviceTokenViewSet(viewsets.ModelViewSet):
    """ViewSet for managing FCM device tokens."""

    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeviceToken.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        token = request.data.get("token")
        platform = request.data.get("platform", "android")

        if not token:
            return Response({"error": "token is required"}, status=status.HTTP_400_BAD_REQUEST)

        device_token, _ = DeviceToken.objects.update_or_create(
            token=token,
            defaults={"user": request.user, "platform": platform, "is_active": True},
        )
        return Response(DeviceTokenSerializer(device_token).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["delete"])
    def deregister(self, request):
        """Deactivate a device token (on logout)."""
        token = request.data.get("token")
        if token:
            DeviceToken.objects.filter(token=token, user=request.user).update(is_active=False)
        return Response({"status": "deregistered"})


class BulkNotificationView(APIView):
    """API view to send bulk notifications."""

    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        """Send notification to multiple users asynchronously via Celery."""
        user_ids = request.data.get("user_ids", [])
        channel = request.data.get("channel", "email")
        subject = request.data.get("subject", "")
        body = request.data.get("body", "")

        if not user_ids:
            return Response(
                {"error": "No users specified"}, status=status.HTTP_400_BAD_REQUEST
            )

        from .tasks import send_bulk_notification_task
        task = send_bulk_notification_task.delay(user_ids, channel, subject, body)

        return Response({"status": "queued", "task_id": task.id})
