from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet, SocialLoginView, LoginView, PasswordResetRequestView, PasswordResetConfirmView, UserProfileView

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('social/', SocialLoginView.as_view(), name='social-login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('', include(router.urls)),
]
