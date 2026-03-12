from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DelegateViewSet, EventRegistrationViewSet, EventViewSet

router = DefaultRouter()
router.register(r"", EventViewSet, basename="event")
router.register(r"registrations", EventRegistrationViewSet, basename="registration")
router.register(r"delegates", DelegateViewSet, basename="delegate")

urlpatterns = [
    path("", include(router.urls)),
]
