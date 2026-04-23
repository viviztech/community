from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InstamojoCallbackView, MembershipCertificateView, PaymentViewSet

router = DefaultRouter()
router.register(r"", PaymentViewSet, basename="payment")

urlpatterns = [
    path("memberships/<int:membership_id>/certificate/", MembershipCertificateView.as_view(), name="membership-certificate"),
    path("callback/", InstamojoCallbackView.as_view(), name="payment-callback"),
    path("", include(router.urls)),
]
