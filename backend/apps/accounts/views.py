"""
Views for User Authentication.
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .models import User
from .serializers import (CustomTokenObtainPairSerializer,
                          PasswordResetConfirmSerializer,
                          PasswordResetRequestSerializer,
                          UserRegistrationSerializer, UserSerializer)

User = get_user_model()


class UserRegistrationView(APIView):
    """Handle user registration."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Send welcome email
            self._send_welcome_email(user)

            return Response(
                {
                    "message": "User registered successfully.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_welcome_email(self, user):
        """Send welcome email to new user."""
        subject = "Welcome to ACTIV Membership Portal"
        message = f"""
        Dear {user.full_name},
        
        Thank you for registering with ACTIV Membership Portal.
        
        Your account has been created successfully.
        
        Best regards,
        ACTIV Team
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )


class LoginView(APIView):
    """Handle user login with email and password."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)

            if not user.check_password(password):
                return Response(
                    {"error": "Invalid credentials."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if not user.is_active:
                return Response(
                    {"error": "Account is deactivated."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Generate tokens
            from rest_framework_simplejwt.tokens import RefreshToken

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserSerializer(user).data,
                }
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token obtain view with additional user info."""

    serializer_class = CustomTokenObtainPairSerializer


class TokenRefreshView(TokenRefreshView):
    """Token refresh view."""

    pass


class UserProfileView(APIView):
    """Get and update user profile."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        # Handle multipart form data for file uploads
        user = request.user

        if "profile_image" in request.FILES:
            user.profile_image = request.FILES["profile_image"]
            user.save()
            return Response(UserSerializer(user).data)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """Request password reset email."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Send reset email
                self._send_password_reset_email(user, uid, token)

                return Response({"message": "Password reset email sent."})
            except User.DoesNotExist:
                # Don't reveal if email exists
                return Response({"message": "Password reset email sent."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _send_password_reset_email(self, user, uid, token):
        """Send password reset email."""
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
        subject = "Password Reset Request"
        message = f"""
        Dear {user.full_name},
        
        You requested a password reset. Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 24 hours.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        ACTIV Team
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )


class PasswordResetConfirmView(APIView):
    """Confirm password reset with token."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data["token"]
            password = serializer.validated_data["password"]

            try:
                uid = urlsafe_base64_decode(token).decode()
                user = User.objects.get(pk=uid)

                if default_token_generator.check_token(user, token):
                    user.set_password(password)
                    user.save()
                    return Response({"message": "Password reset successful."})
                return Response(
                    {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
                )
            except (User.DoesNotExist, ValueError):
                return Response(
                    {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Handle user logout (blacklist token)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                from rest_framework_simplejwt.tokens import RefreshToken

                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Logged out successfully."})
        except Exception as e:
            return Response({"message": "Logged out successfully."})


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        return UserSerializer

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get current user info."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class SocialLoginView(APIView):
    """Handle social media login."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Process social login."""
        provider = request.data.get("provider")
        access_token = request.data.get("access_token")

        # In production, use python-social-auth or directly verify token
        # For now, return a placeholder response
        return Response(
            {
                "message": "Social login integration - Configure provider credentials",
                "provider": provider,
            }
        )
