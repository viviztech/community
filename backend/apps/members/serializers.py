"""
Serializers for Member models.
"""

from rest_framework import serializers
from .models import Member, GeographicArea, SisterConcern, GovernmentSchemeBenefit


class GeographicAreaSerializer(serializers.ModelSerializer):
    """Serializer for geographic areas."""
    
    class Meta:
        model = GeographicArea
        fields = ['id', 'name', 'area_type', 'parent', 'code', 'is_active']


class SisterConcernSerializer(serializers.ModelSerializer):
    """Serializer for sister concerns."""
    
    class Meta:
        model = SisterConcern
        fields = [
            'id', 'name', 'constitution', 'business_type',
            'turnover_range', 'is_active'
        ]


class SisterConcernCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sister concerns."""
    
    class Meta:
        model = SisterConcern
        fields = ['name', 'constitution', 'business_type', 'turnover_range']


class GovernmentSchemeBenefitSerializer(serializers.ModelSerializer):
    """Serializer for government scheme benefits."""
    
    class Meta:
        model = GovernmentSchemeBenefit
        fields = ['id', 'scheme_name', 'benefit_details', 'availed_year', 'is_active']


class GovernmentSchemeBenefitCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating government scheme benefits."""
    
    class Meta:
        model = GovernmentSchemeBenefit
        fields = ['scheme_name', 'benefit_details', 'availed_year']


class MemberSerializer(serializers.ModelSerializer):
    """Serializer for member details."""
    
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    sister_concerns = SisterConcernSerializer(many=True, read_only=True)
    scheme_benefits = GovernmentSchemeBenefitSerializer(many=True, read_only=True)
    
    class Meta:
        model = Member
        fields = [
            'id', 'user', 'email', 'full_name', 'phone_number',
            # Personal Details
            'date_of_birth', 'gender', 'religion', 'caste', 'social_category',
            # Address
            'address_line_1', 'address_line_2', 'block', 'district', 'state', 'pincode',
            # Education
            'educational_qualification', 'occupation',
            # Business Details
            'is_doing_business', 'organization_name', 'constitution', 'business_type',
            'business_activities', 'business_commencement_year', 'number_of_employees',
            # Government Registrations
            'msme_registered', 'msme_number', 'nsic_registered', 'nsic_number',
            'gst_registered', 'gst_number', 'ie_code',
            # Taxation
            'pan_number', 'udyam_number', 'has_filed_itr', 'itr_filing_years',
            # Financial
            'turnover_range',
            # Other Memberships
            'member_of_other_chambers', 'other_chamber_details',
            # Profile Completeness
            'profile_completion_percentage', 'profile_completed_at',
            # Related
            'sister_concerns', 'scheme_benefits',
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class MemberCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating members."""
    
    sister_concerns = SisterConcernCreateSerializer(many=True, required=False)
    scheme_benefits = GovernmentSchemeBenefitCreateSerializer(many=True, required=False)
    
    class Meta:
        model = Member
        fields = [
            # Personal Details
            'date_of_birth', 'gender', 'religion', 'caste', 'social_category',
            # Address
            'address_line_1', 'address_line_2', 'block', 'district', 'state', 'pincode',
            # Education
            'educational_qualification', 'occupation',
            # Business Details
            'is_doing_business', 'organization_name', 'constitution', 'business_type',
            'business_activities', 'business_commencement_year', 'number_of_employees',
            # Government Registrations
            'msme_registered', 'msme_number', 'nsic_registered', 'nsic_number',
            'gst_registered', 'gst_number', 'ie_code',
            # Taxation
            'pan_number', 'udyam_number', 'has_filed_itr', 'itr_filing_years',
            # Financial
            'turnover_range',
            # Other Memberships
            'member_of_other_chambers', 'other_chamber_details',
            # Related
            'sister_concerns', 'scheme_benefits'
        ]
    
    def create(self, validated_data):
        sister_concerns_data = validated_data.pop('sister_concerns', [])
        scheme_benefits_data = validated_data.pop('scheme_benefits', [])
        
        member = Member.objects.create(**validated_data)
        
        # Create sister concerns
        for concern_data in sister_concerns_data:
            SisterConcern.objects.create(member=member, **concern_data)
        
        # Create scheme benefits
        for benefit_data in scheme_benefits_data:
            GovernmentSchemeBenefit.objects.create(member=member, **benefit_data)
        
        # Calculate profile completion
        member.calculate_profile_completion()
        member.save()
        
        return member
    
    def update(self, instance, validated_data):
        sister_concerns_data = validated_data.pop('sister_concerns', None)
        scheme_benefits_data = validated_data.pop('scheme_benefits', None)
        
        # Update member fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update sister concerns if provided
        if sister_concerns_data is not None:
            instance.sister_concerns.all().delete()
            for concern_data in sister_concerns_data:
                SisterConcern.objects.create(member=instance, **concern_data)
        
        # Update scheme benefits if provided
        if scheme_benefits_data is not None:
            instance.scheme_benefits.all().delete()
            for benefit_data in scheme_benefits_data:
                GovernmentSchemeBenefit.objects.create(member=instance, **benefit_data)
        
        # Recalculate profile completion
        instance.calculate_profile_completion()
        instance.save()
        
        return instance


class MemberListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for member listing."""
    
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    block_name = serializers.CharField(source='block.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    
    class Meta:
        model = Member
        fields = [
            'id', 'email', 'full_name', 'social_category',
            'block_name', 'district_name', 'organization_name',
            'profile_completion_percentage', 'created_at'
        ]
