"""
Serializers for User Authentication.
"""

from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import AdminProfile, User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    phone_number = PhoneNumberField(required=False, allow_null=True, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        if not validated_data.get('phone_number'):
            validated_data.pop('phone_number', None)
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""

    full_name = serializers.CharField(read_only=True)
    admin_role = serializers.SerializerMethodField()
    admin_area = serializers.SerializerMethodField()
    admin_area_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "full_name",
            "profile_image",
            "email_verified",
            "phone_verified",
            "social_provider",
            "is_superuser",
            "is_staff",
            "admin_role",
            "admin_area",
            "admin_area_id",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "email", "date_joined", "last_login", "is_superuser", "is_staff"]

    def get_admin_role(self, obj):
        """Return the active admin level string, or None."""
        if obj.is_superuser:
            return "super"
        profile = getattr(obj, "admin_profile", None)
        if profile and profile.status == "active":
            return profile.admin_level
        return None

    def get_admin_area(self, obj):
        profile = getattr(obj, "admin_profile", None)
        if profile and profile.status == "active" and profile.area:
            return profile.area.name
        return None

    def get_admin_area_id(self, obj):
        profile = getattr(obj, "admin_profile", None)
        if profile and profile.status == "active" and profile.area:
            return str(profile.area.id)
        return None


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom token serializer with additional user info."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["email"] = user.email
        token["full_name"] = user.full_name
        token["is_staff"] = user.is_staff

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user info to response
        data["user"] = UserSerializer(self.user).data

        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""

    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs


class PhoneOTPRequestSerializer(serializers.Serializer):
    """Serializer for phone OTP request."""

    phone_number = PhoneNumberField()


class PhoneOTPVerifySerializer(serializers.Serializer):
    """Serializer for phone OTP verification."""

    phone_number = PhoneNumberField()
    otp = serializers.CharField(max_length=6)


class AdminProfileSerializer(serializers.ModelSerializer):
    """Serializer for AdminProfile — read-only view."""

    admin_level_display = serializers.CharField(source="get_admin_level_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    area_name = serializers.SerializerMethodField()
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    nominated_by_email = serializers.EmailField(source="nominated_by.email", read_only=True, allow_null=True)

    class Meta:
        model = AdminProfile
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "admin_level",
            "admin_level_display",
            "area",
            "area_name",
            "status",
            "status_display",
            "nominated_by",
            "nominated_by_email",
            "nomination_notes",
            "activated_at",
            "revoked_at",
            "created_at",
        ]
        read_only_fields = ["id", "user", "activated_at", "revoked_at", "created_at"]

    def get_area_name(self, obj):
        return obj.area.name if obj.area else None


class AdminNominationSerializer(serializers.Serializer):
    """Payload for nominating a new admin."""

    user_id = serializers.UUIDField()
    admin_level = serializers.ChoiceField(choices=AdminProfile.AdminLevel.choices)
    area_id = serializers.UUIDField(required=False, allow_null=True)
    nomination_notes = serializers.CharField(required=False, allow_blank=True)


class AdminRevokeSerializer(serializers.Serializer):
    """Payload for revoking an admin."""

    revoke_reason = serializers.CharField(required=False, allow_blank=True)
