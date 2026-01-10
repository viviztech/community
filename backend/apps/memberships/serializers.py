"""
Serializers for Membership Tiers and Memberships.
"""

from rest_framework import serializers
from .models import MembershipTier, Membership


class MembershipTierSerializer(serializers.ModelSerializer):
    """Serializer for membership tiers."""
    
    class Meta:
        model = MembershipTier
        fields = [
            'id', 'name', 'tier_type', 'description',
            'yearly_price', 'lifetime_price', 'features',
            'is_active', 'sort_order'
        ]
        read_only_fields = ['id']


class MembershipSerializer(serializers.ModelSerializer):
    """Serializer for active memberships."""
    
    tier_name = serializers.CharField(source='tier.name', read_only=True)
    member_name = serializers.CharField(source='member.user.full_name', read_only=True)
    member_email = serializers.EmailField(source='member.user.email', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Membership
        fields = [
            'id', 'member', 'member_name', 'member_email',
            'tier', 'tier_name', 'status', 'membership_type',
            'start_date', 'end_date', 'is_valid',
            'certificate_number', 'certificate_issued_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'certificate_number', 'certificate_issued_at',
            'created_at', 'updated_at'
        ]


class MembershipCreateSerializer(serializers.Serializer):
    """Serializer for creating a new membership."""
    
    member_id = serializers.UUIDField()
    tier_id = serializers.UUIDField()
    membership_type = serializers.ChoiceField(choices=['yearly', 'lifetime'])
    
    def validate_tier_id(self, value):
        try:
            tier = MembershipTier.objects.get(id=value, is_active=True)
        except MembershipTier.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive membership tier")
        return value
    
    def validate_member_id(self, value):
        try:
            from apps.members.models import Member
            member = Member.objects.get(id=value)
        except Member.DoesNotExist:
            raise serializers.ValidationError("Invalid member ID")
        return value


class MembershipRenewSerializer(serializers.Serializer):
    """Serializer for renewing a membership."""
    
    membership_type = serializers.ChoiceField(choices=['yearly', 'lifetime'])
