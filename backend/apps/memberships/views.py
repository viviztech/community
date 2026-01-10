"""
Views for Membership Tiers and Memberships.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from .models import MembershipTier, Membership
from .serializers import (
    MembershipTierSerializer,
    MembershipSerializer,
    MembershipCreateSerializer,
    MembershipRenewSerializer
)


class MembershipTierViewSet(viewsets.ModelViewSet):
    """ViewSet for membership tiers."""
    
    queryset = MembershipTier.objects.filter(is_active=True)
    serializer_class = MembershipTierSerializer
    permission_classes = [permissions.AllowAny]  # Public read access
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Order by sort_order
        return queryset.order_by('sort_order')
    
    @action(detail=False, methods=['get'])
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
        if self.action == 'create':
            return MembershipCreateSerializer
        return MembershipSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Membership.objects.all()
        if hasattr(user, 'member_profile'):
            return Membership.objects.filter(member=user.member_profile)
        return Membership.objects.none()
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """Renew a membership."""
        membership = self.get_object()
        serializer = MembershipRenewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from django.utils import timezone
        from datetime import timedelta
        
        if serializer.validated_data['membership_type'] == 'yearly':
            membership.membership_type = 'yearly'
            membership.end_date = timezone.now().date() + timedelta(days=365)
        else:
            membership.membership_type = 'lifetime'
            membership.end_date = None
        
        membership.save()
        return Response(MembershipSerializer(membership).data)
    
    @action(detail=True, methods=['get'])
    def certificate(self, request, pk=None):
        """Get membership certificate details."""
        membership = self.get_object()
        return Response({
            'certificate_number': membership.certificate_number,
            'member_name': membership.member.user.full_name,
            'tier': membership.tier.name,
            'start_date': membership.start_date,
            'end_date': membership.end_date,
            'issued_at': membership.certificate_issued_at
        })
