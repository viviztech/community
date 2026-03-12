from django.contrib import admin

from .models import Notification, NotificationPreference, NotificationTemplate


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "channel", "event_type", "is_active")
    list_filter = ("channel", "event_type", "is_active")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "channel", "status", "created_at")
    list_filter = ("channel", "status")
    raw_id_fields = ("user", "template")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "email_enabled", "sms_enabled", "whatsapp_enabled")
    raw_id_fields = ("user",)
