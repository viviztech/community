"""
Member Models for ACTIV Membership Portal.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class GeographicArea(models.Model):
    """Geographic areas for administrative hierarchy."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    area_type = models.CharField(
        max_length=20,
        choices=[
            ('block', 'Block'),
            ('district', 'District'),
            ('state', 'State'),
        ]
    )
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE,
        related_name='children'
    )
    code = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'geographic_areas'
        verbose_name = _('Geographic Area')
        verbose_name_plural = _('Geographic Areas')
        ordering = ['area_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_area_type_display()})"


class Member(models.Model):
    """
    Member model extending User with detailed profile information.
    """
    
    class SocialCategory(models.TextChoices):
        SC = 'SC', _('Scheduled Caste')
        ST = 'ST', _('Scheduled Tribe')
        CONVERTED_CHRISTIAN = 'CC', _('Converted Christians from SC')
        OBC = 'OBC', _('Other Backward Class')
        OTHERS = 'O', _('Others')
    
    class BusinessType(models.TextChoices):
        MANUFACTURING = 'M', _('Manufacturing')
        SERVICE = 'S', _('Service')
        TRADER = 'T', _('Trader')
        DEALER = 'D', _('Dealer')
    
    class Constitution(models.TextChoices):
        PROPRIETORSHIP = 'PROP', _('Proprietorship')
        PARTNERSHIP = 'PART', _('Partnership')
        PRIVATE_LIMITED = 'PVT', _('Private Limited')
        PUBLIC_LIMITED = 'PUB', _('Public Limited')
        OPC = 'OPC', _('One Person Company')
        LLP = 'LLP', _('Limited Liability Partnership')
        TRUST = 'TRUST', _('Trust')
        SOCIETY = 'SOC', _('Society')
    
    class TurnoverRange(models.TextChoices):
        LESS_THAN_40L = '<40L', _('< 40 Lakhs')
        LESS_THAN_1CR = '<1CR', _('40 Lakhs - 1 Crore')
        LESS_THAN_5CR = '<5CR', _('1 - 5 Crore')
        LESS_THAN_50CR = '<50CR', _('5 - 50 Crore')
        LESS_THAN_250CR = '<250CR', _('50 - 250 Crore')
        LESS_THAN_500CR = '<500CR', _('250 - 500 Crore')
        MORE_THAN_1000CR = '>1000CR', _('> 1000 Crore')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='member_profile'
    )
    
    # Personal Details
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10, choices=[
            ('M', 'Male'), ('F', 'Female'), ('O', 'Other')
        ], null=True, blank=True
    )
    religion = models.CharField(max_length=50, null=True, blank=True)
    caste = models.CharField(max_length=50, null=True, blank=True)
    social_category = models.CharField(
        max_length=3, choices=SocialCategory.choices, null=True, blank=True
    )
    
    # Address
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    block = models.ForeignKey(
        GeographicArea, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='block_members', limit_choices_to={'area_type': 'block'}
    )
    district = models.ForeignKey(
        GeographicArea, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='district_members', limit_choices_to={'area_type': 'district'}
    )
    state = models.ForeignKey(
        GeographicArea, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='state_members', limit_choices_to={'area_type': 'state'}
    )
    pincode = models.CharField(max_length=6, null=True, blank=True)
    
    # Education & Professional
    educational_qualification = models.CharField(max_length=100, null=True, blank=True)
    occupation = models.CharField(max_length=100, null=True, blank=True)
    
    # Business Details
    is_doing_business = models.BooleanField(default=False)
    organization_name = models.CharField(max_length=255, null=True, blank=True)
    constitution = models.CharField(
        max_length=10, choices=Constitution.choices, null=True, blank=True
    )
    business_type = models.CharField(
        max_length=1, choices=BusinessType.choices, null=True, blank=True
    )
    business_activities = models.TextField(null=True, blank=True)
    business_commencement_year = models.IntegerField(null=True, blank=True)
    number_of_employees = models.IntegerField(null=True, blank=True)
    
    # Government Registrations
    msme_registered = models.BooleanField(default=False)
    msme_number = models.CharField(max_length=50, null=True, blank=True)
    nsic_registered = models.BooleanField(default=False)
    nsic_number = models.CharField(max_length=50, null=True, blank=True)
    gst_registered = models.BooleanField(default=False)
    gst_number = models.CharField(max_length=50, null=True, blank=True)
    ie_code = models.CharField(max_length=50, null=True, blank=True)
    
    # Taxation
    pan_number = models.CharField(max_length=10, null=True, blank=True)
    udyam_number = models.CharField(max_length=50, null=True, blank=True)
    has_filed_itr = models.BooleanField(default=False)
    itr_filing_years = models.IntegerField(null=True, blank=True)
    
    # Financial
    turnover_range = models.CharField(
        max_length=10, choices=TurnoverRange.choices, null=True, blank=True
    )
    
    # Other Memberships
    member_of_other_chambers = models.BooleanField(default=False)
    other_chamber_details = models.TextField(null=True, blank=True)
    
    # Profile Completeness
    profile_completion_percentage = models.IntegerField(default=0)
    profile_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'members'
        verbose_name = _('Member')
        verbose_name_plural = _('Members')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['block', 'district', 'state']),
            models.Index(fields=['social_category']),
            models.Index(fields=['is_doing_business']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.user.email})"
    
    def calculate_profile_completion(self):
        """Calculate profile completion percentage."""
        fields = [
            'date_of_birth', 'gender', 'social_category', 'address_line_1',
            'block', 'district', 'state', 'pincode',
            'educational_qualification', 'organization_name', 'constitution',
            'business_type', 'pan_number', 'gst_number'
        ]
        
        completed = 0
        total = len(fields)
        
        for field in fields:
            value = getattr(self, field, None)
            if value:
                completed += 1
        
        percentage = int((completed / total) * 100)
        self.profile_completion_percentage = percentage
        
        if percentage >= 80:
            self.profile_completed_at = timezone.now()
        
        return percentage


class SisterConcern(models.Model):
    """Sister concerns of a member's business."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='sister_concerns'
    )
    name = models.CharField(max_length=255)
    constitution = models.CharField(
        max_length=10, choices=Member.Constitution.choices
    )
    business_type = models.CharField(
        max_length=1, choices=Member.BusinessType.choices
    )
    turnover_range = models.CharField(
        max_length=10, choices=Member.TurnoverRange.choices
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'sister_concerns'
        verbose_name = _('Sister Concern')
        verbose_name_plural = _('Sister Concerns')
    
    def __str__(self):
        return f"{self.name} (Sister concern of {self.member.user.full_name})"


class GovernmentSchemeBenefit(models.Model):
    """Government scheme benefits availed by member."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='scheme_benefits'
    )
    scheme_name = models.CharField(max_length=255)
    benefit_details = models.TextField()
    availed_year = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'government_scheme_benefits'
        verbose_name = _('Government Scheme Benefit')
        verbose_name_plural = _('Government Scheme Benefits')
    
    def __str__(self):
        return f"{self.scheme_name} ({self.member.user.full_name})"
