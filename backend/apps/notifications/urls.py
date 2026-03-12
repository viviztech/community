from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (BulkNotificationView, NotificationPreferenceViewSet,
                    NotificationTemplateViewSet, NotificationViewSet,
                    SendNotificationView)

router = DefaultRouter()
router.register(r"templates", NotificationTemplateViewSet, basename="template")
router.register(r"preferences", NotificationPreferenceViewSet, basename="preference")
router.register(r"", NotificationViewSet, basename="notification")

urlpatterns = [
    path("", include(router.urls)),
    path("send/", SendNotificationView.as_view(), name="send-notification"),
    path("send/bulk/", BulkNotificationView.as_view(), name="bulk-notification"),
]
