"""
Views for Membership Tiers and Memberships.
"""

from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Membership, MembershipTier
from .serializers import (MembershipCreateSerializer,
                          MembershipRenewSerializer, MembershipSerializer,
                          MembershipTierSerializer)


class MembershipTierViewSet(viewsets.ModelViewSet):
    """ViewSet for membership tiers."""

    queryset = MembershipTier.objects.filter(is_active=True)
    serializer_class = MembershipTierSerializer
    permission_classes = [permissions.AllowAny]  # Public read access

    def get_queryset(self):
        queryset = super().get_queryset()
        # Order by sort_order
        return queryset.order_by("sort_order")

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get all active membership tiers."""
        tiers = self.get_queryset()
        serializer = self.get_serializer(tiers, many=True)
        return Response(serializer.data)


class MembershipViewSet(viewsets.ModelViewSet):
    """ViewSet for memberships."""

    queryset = Membership.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return MembershipCreateSerializer
        return MembershipSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Membership.objects.all()
        if hasattr(user, "member_profile"):
            return Membership.objects.filter(member=user.member_profile)
        return Membership.objects.none()

    @action(detail=True, methods=["post"])
    def renew(self, request, pk=None):
        """Renew a membership."""
        membership = self.get_object()
        serializer = MembershipRenewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from datetime import timedelta

        from django.utils import timezone

        if serializer.validated_data["membership_type"] == "yearly":
            membership.membership_type = "yearly"
            membership.end_date = timezone.now().date() + timedelta(days=365)
        else:
            membership.membership_type = "lifetime"
            membership.end_date = None

        membership.save()
        return Response(MembershipSerializer(membership).data)

    @action(detail=True, methods=["get"])
    def certificate(self, request, pk=None):
        """Get membership certificate details."""
        membership = self.get_object()
        return Response(
            {
                "certificate_number": membership.certificate_number,
                "member_name": membership.member.user.full_name,
                "tier": membership.tier.name,
                "start_date": membership.start_date,
                "end_date": membership.end_date,
                "issued_at": membership.certificate_issued_at,
            }
        )

    @action(detail=False, methods=["post"], url_path="apply")
    def apply_for_membership(self, request):
        """Apply for a membership."""
        from datetime import timedelta

        from django.utils import timezone

        tier_id = request.data.get("tier_id")
        membership_type = request.data.get("membership_type", "yearly")

        if not tier_id:
            return Response(
                {"error": "tier_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            tier = MembershipTier.objects.get(id=tier_id, is_active=True)
        except MembershipTier.DoesNotExist:
            return Response(
                {"error": "Invalid tier"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get member profile
        if not hasattr(request.user, "member_profile"):
            return Response(
                {"error": "Member profile not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member = request.user.member_profile

        # Check if already has active membership
        existing = Membership.objects.filter(member=member, status="active").first()
        if existing:
            return Response(
                {"error": "Already have an active membership"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate dates
        start_date = timezone.now().date()
        end_date = (
            start_date + timedelta(days=365) if membership_type == "yearly" else None
        )

        # Create membership
        membership = Membership.objects.create(
            member=member,
            tier=tier,
            membership_type=membership_type,
            start_date=start_date,
            end_date=end_date,
            status="pending",  # Will be updated after payment
        )

        return Response(
            MembershipSerializer(membership).data, status=status.HTTP_201_CREATED
        )
