from django.contrib import admin
from .models import MembershipTier, Membership


@admin.register(MembershipTier)
class MembershipTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier_type', 'yearly_price', 'lifetime_price', 'is_active')
    list_filter = ('tier_type', 'is_active')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('member', 'tier', 'status', 'membership_type', 'start_date', 'end_date')
    list_filter = ('status', 'membership_type')
    raw_id_fields = ('member', 'tier', 'payment')
