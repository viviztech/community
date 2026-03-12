from django.contrib import admin

from .models import (GeographicArea, GovernmentSchemeBenefit, Member,
                     SisterConcern)


@admin.register(GeographicArea)
class GeographicAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "area_type", "parent", "code", "is_active")
    list_filter = ("area_type", "is_active")
    search_fields = ("name", "code")


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("user", "social_category", "is_doing_business", "created_at")
    list_filter = ("social_category", "is_doing_business", "gender")
    search_fields = ("user__email", "user__first_name", "udyam_number", "pan_number")
    raw_id_fields = ("user", "block", "district", "state")


@admin.register(SisterConcern)
class SisterConcernAdmin(admin.ModelAdmin):
    list_display = ("member", "name", "constitution", "is_active")
    search_fields = ("name", "member__user__email")
    raw_id_fields = ("member",)


@admin.register(GovernmentSchemeBenefit)
class GovernmentSchemeBenefitAdmin(admin.ModelAdmin):
    list_display = ("member", "scheme_name", "availed_year", "is_active")
    search_fields = ("scheme_name", "member__user__email")
    raw_id_fields = ("member",)
