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
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import AdminProfile, User
from .permissions import IsAnyAdmin, IsDistrictAdmin, IsSuperAdmin, IsStateAdmin
from .serializers import (
    AdminNominationSerializer,
    AdminProfileSerializer,
    AdminRevokeSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

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

            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "message": "User registered successfully.",
                    "user": UserSerializer(user).data,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
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
            uid_encoded = serializer.validated_data["uid"]
            token = serializer.validated_data["token"]
            password = serializer.validated_data["password"]

            try:
                uid = urlsafe_base64_decode(uid_encoded).decode()
                user = User.objects.get(pk=uid)

                if default_token_generator.check_token(user, token):
                    user.set_password(password)
                    user.save()
                    return Response({"message": "Password reset successful."})
                return Response(
                    {"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST
                )
            except (User.DoesNotExist, ValueError):
                return Response(
                    {"error": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST
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


class OTPSendView(APIView):
    """Send OTP to a user's phone number."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.phone_number:
            return Response(
                {"error": "No phone number on file. Update your profile first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = user.generate_otp()

        # Send via SMS
        try:
            from apps.notifications.views import TwilioService
            TwilioService.send_sms(str(user.phone_number), f"Your ACTIV OTP is: {otp}. Valid for 10 minutes.")
        except Exception:
            pass

        return Response({"message": "OTP sent to your registered phone number."})


class OTPVerifyView(APIView):
    """Verify OTP submitted by user."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        otp = request.data.get("otp")
        if not otp:
            return Response(
                {"error": "OTP is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.verify_otp(otp):
            return Response({"message": "Phone number verified successfully."})

        return Response(
            {"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST
        )


class SocialLoginView(APIView):
    """Handle social media login (Google / Facebook)."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        provider = request.data.get("provider", "").lower()
        access_token = request.data.get("access_token")

        if not provider or not access_token:
            return Response(
                {"error": "provider and access_token are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_info = self._verify_token(provider, access_token)
        if not user_info:
            return Response(
                {"error": "Invalid or expired access token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email = user_info.get("email")
        if not email:
            return Response(
                {"error": "Could not retrieve email from provider."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "first_name": user_info.get("given_name", ""),
                "last_name": user_info.get("family_name", ""),
                "social_provider": provider,
                "social_user_id": user_info.get("sub") or user_info.get("id", ""),
                "email_verified": True,
                "username": email,
            },
        )

        if not created:
            user.social_provider = provider
            user.social_user_id = user_info.get("sub") or user_info.get("id", "")
            user.save(update_fields=["social_provider", "social_user_id"])

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
                "created": created,
            }
        )

    def _verify_token(self, provider, access_token):
        """Verify token with the provider and return user info dict."""
        import requests as req
        try:
            if provider == "google":
                resp = req.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10,
                )
                if resp.status_code == 200:
                    return resp.json()

            elif provider == "facebook":
                resp = req.get(
                    "https://graph.facebook.com/me",
                    params={"fields": "id,name,email,first_name,last_name", "access_token": access_token},
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    data["sub"] = data.get("id")
                    data["given_name"] = data.get("first_name", "")
                    data["family_name"] = data.get("last_name", "")
                    return data
        except Exception:
            pass
        return None


# ──────────────────────────────────────────────
#  Admin Role / Nomination Management
# ──────────────────────────────────────────────

class AdminNominateView(APIView):
    """
    Nominate a user as an admin.
    - Super Admin can nominate any level.
    - State Admin can nominate District or Block admins within their state.
    - District Admin can nominate Block admins within their district.
    """

    permission_classes = [IsAnyAdmin]

    def post(self, request):
        serializer = AdminNominationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        nominator = request.user
        nominator_admin = getattr(nominator, "admin_profile", None)
        is_super = nominator.is_superuser or (nominator_admin and nominator_admin.admin_level == "super")

        target_level = data["admin_level"]

        # Enforce nomination hierarchy
        if not is_super:
            if nominator_admin is None or nominator_admin.status != "active":
                return Response({"error": "Your admin role is not active."}, status=status.HTTP_403_FORBIDDEN)
            level_rank = {"block": 1, "district": 2, "state": 3, "super": 4}
            if level_rank.get(target_level, 0) >= level_rank.get(nominator_admin.admin_level, 0):
                return Response(
                    {"error": f"A {nominator_admin.get_admin_level_display()} can only nominate lower-level admins."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # Find target user
        try:
            target_user = User.objects.get(pk=data["user_id"])
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if target_user.is_superuser:
            return Response({"error": "Cannot assign an admin role to a superuser."}, status=status.HTTP_400_BAD_REQUEST)

        # Area validation
        area = None
        if target_level != "super":
            area_id = data.get("area_id")
            if not area_id:
                return Response({"error": "area_id is required for non-super admin levels."}, status=status.HTTP_400_BAD_REQUEST)
            from apps.members.models import GeographicArea
            try:
                area = GeographicArea.objects.get(pk=area_id, is_active=True)
            except GeographicArea.DoesNotExist:
                return Response({"error": "Geographic area not found."}, status=status.HTTP_404_NOT_FOUND)

            area_type_map = {"block": "block", "district": "district", "state": "state"}
            if area.area_type != area_type_map[target_level]:
                return Response(
                    {"error": f"Area type mismatch: expected {area_type_map[target_level]}, got {area.area_type}."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Remove any existing admin profile before creating new (OneToOne constraint)
        existing = getattr(target_user, "admin_profile", None)
        if existing:
            existing.delete()

        admin_profile = AdminProfile.objects.create(
            user=target_user,
            admin_level=target_level,
            area=area,
            nominated_by=nominator,
            nomination_notes=data.get("nomination_notes", ""),
            status=AdminProfile.Status.PENDING,
        )

        # Super admin nominations are auto-activated if nominator is superuser
        if is_super and nominator.is_superuser:
            admin_profile.activate(approved_by_user=nominator)

        return Response(AdminProfileSerializer(admin_profile).data, status=status.HTTP_201_CREATED)


class AdminApproveView(APIView):
    """Approve a pending admin nomination."""

    permission_classes = [IsAnyAdmin]

    def post(self, request, pk):
        try:
            admin_profile = AdminProfile.objects.get(pk=pk, status=AdminProfile.Status.PENDING)
        except AdminProfile.DoesNotExist:
            return Response({"error": "Pending admin profile not found."}, status=status.HTTP_404_NOT_FOUND)

        approver = request.user
        approver_admin = getattr(approver, "admin_profile", None)
        is_super = approver.is_superuser or (approver_admin and approver_admin.admin_level == "super")

        if not is_super:
            level_rank = {"block": 1, "district": 2, "state": 3, "super": 4}
            if level_rank.get(admin_profile.admin_level, 0) >= level_rank.get(getattr(approver_admin, "admin_level", "block"), 0):
                return Response({"error": "You do not have permission to approve this nomination."}, status=status.HTTP_403_FORBIDDEN)

        admin_profile.activate(approved_by_user=approver)
        return Response(AdminProfileSerializer(admin_profile).data)


class AdminRevokeView(APIView):
    """Revoke an active admin role."""

    permission_classes = [IsAnyAdmin]

    def post(self, request, pk):
        try:
            admin_profile = AdminProfile.objects.get(pk=pk, status=AdminProfile.Status.ACTIVE)
        except AdminProfile.DoesNotExist:
            return Response({"error": "Active admin profile not found."}, status=status.HTTP_404_NOT_FOUND)

        approver = request.user
        approver_admin = getattr(approver, "admin_profile", None)
        is_super = approver.is_superuser or (approver_admin and approver_admin.admin_level == "super")

        if not is_super:
            level_rank = {"block": 1, "district": 2, "state": 3, "super": 4}
            if level_rank.get(admin_profile.admin_level, 0) >= level_rank.get(getattr(approver_admin, "admin_level", "block"), 0):
                return Response({"error": "You do not have permission to revoke this admin."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AdminRevokeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin_profile.revoke(reason=serializer.validated_data.get("revoke_reason", ""))
        return Response(AdminProfileSerializer(admin_profile).data)


class AdminListView(APIView):
    """List all admin profiles visible to the requesting admin."""

    permission_classes = [IsAnyAdmin]

    def get(self, request):
        user = request.user
        queryset = AdminProfile.objects.select_related("user", "area", "nominated_by").all()

        if not user.is_superuser:
            admin = getattr(user, "admin_profile", None)
            if admin and admin.status == "active":
                if admin.admin_level == "state":
                    # State admin sees district + block admins in their state's sub-areas
                    queryset = queryset.filter(admin_level__in=["district", "block"])
                elif admin.admin_level == "district":
                    queryset = queryset.filter(admin_level="block")
                else:
                    return Response([])

        status_filter = request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        level_filter = request.query_params.get("level")
        if level_filter:
            queryset = queryset.filter(admin_level=level_filter)

        return Response(AdminProfileSerializer(queryset, many=True).data)
