from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AdminApproveView,
    AdminListView,
    AdminNominateView,
    AdminRevokeView,
    LoginView,
    LogoutView,
    OTPSendView,
    OTPVerifyView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    SocialLoginView,
    UserProfileView,
    UserRegistrationView,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("otp/send/", OTPSendView.as_view(), name="otp-send"),
    path("otp/verify/", OTPVerifyView.as_view(), name="otp-verify"),
    path(
        "password/reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("social/", SocialLoginView.as_view(), name="social-login"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    # Admin nomination endpoints
    path("admins/", AdminListView.as_view(), name="admin-list"),
    path("admins/nominate/", AdminNominateView.as_view(), name="admin-nominate"),
    path("admins/<uuid:pk>/approve/", AdminApproveView.as_view(), name="admin-approve"),
    path("admins/<uuid:pk>/revoke/", AdminRevokeView.as_view(), name="admin-revoke"),
    path("", include(router.urls)),
]
