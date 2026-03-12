from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GeographicAreaViewSet, MemberViewSet

router = DefaultRouter()
router.register(r"", MemberViewSet, basename="member")
router.register(r"areas", GeographicAreaViewSet, basename="area")

urlpatterns = [
    path("", include(router.urls)),
]
