"""
Serializers for Member models.
"""

from rest_framework import serializers

from .models import GeographicArea, GovernmentSchemeBenefit, Member, MemberDocument, SisterConcern

# Fields required per member type for profile completion guidance
REQUIRED_DOCS_BY_TYPE = {
    "individual": ["aadhaar", "pan"],
    "shg": ["aadhaar", "pan", "shg_reg", "shg_bank"],
    "fpo": ["aadhaar", "pan", "fpo_reg", "fpo_bylaw"],
}


class GeographicAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeographicArea
        fields = ["id", "name", "area_type", "parent", "code", "is_active"]


class SisterConcernSerializer(serializers.ModelSerializer):
    class Meta:
        model = SisterConcern
        fields = ["id", "name", "constitution", "business_type", "turnover_range", "is_active"]


class SisterConcernCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SisterConcern
        fields = ["name", "constitution", "business_type", "turnover_range"]


class GovernmentSchemeBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernmentSchemeBenefit
        fields = ["id", "scheme_name", "benefit_details", "availed_year", "is_active"]


class GovernmentSchemeBenefitCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernmentSchemeBenefit
        fields = ["scheme_name", "benefit_details", "availed_year"]


class MemberDocumentSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source="get_document_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = MemberDocument
        fields = [
            "id", "document_type", "document_type_display",
            "file", "original_filename",
            "status", "status_display", "notes",
            "uploaded_at", "reviewed_at",
        ]
        read_only_fields = ["id", "status", "uploaded_at", "reviewed_at"]


class MemberSerializer(serializers.ModelSerializer):
    """Full member profile serializer (read)."""

    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    member_type_display = serializers.CharField(source="get_member_type_display", read_only=True)
    sister_concerns = SisterConcernSerializer(many=True, read_only=True)
    scheme_benefits = GovernmentSchemeBenefitSerializer(many=True, read_only=True)
    documents = MemberDocumentSerializer(many=True, read_only=True)
    required_documents = serializers.SerializerMethodField()
    document_verification_status = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            "id", "user", "email", "full_name", "phone_number",
            # Member type
            "member_type", "member_type_display",
            # Personal Details
            "date_of_birth", "gender", "religion", "caste", "social_category",
            # Address
            "address_line_1", "address_line_2", "block", "district", "state", "pincode",
            # Education
            "educational_qualification", "occupation",
            # Business Details (Individual)
            "is_doing_business", "organization_name", "constitution", "business_type",
            "business_activities", "business_commencement_year", "number_of_employees",
            # Government Registrations
            "msme_registered", "msme_number", "nsic_registered", "nsic_number",
            "gst_registered", "gst_number", "ie_code",
            # Taxation
            "pan_number", "udyam_number", "has_filed_itr", "itr_filing_years",
            # Financial
            "turnover_range",
            # SHG fields
            "shg_name", "shg_registration_number", "shg_formation_date",
            "shg_member_count", "shg_bank_linked", "shg_bank_name",
            "shg_bank_account_number", "shg_promoting_institution", "shg_federation_name",
            # FPO fields
            "fpo_name", "fpo_registration_number", "fpo_registration_date",
            "fpo_farmer_count", "fpo_total_land_area_acres", "fpo_crop_types",
            "fpo_annual_turnover", "fpo_ceo_name", "fpo_ceo_phone", "fpo_commodity",
            # Other
            "member_of_other_chambers", "other_chamber_details",
            # Approval
            "is_approved", "approved_at",
            # Profile Completeness
            "profile_completion_percentage", "profile_completed_at",
            # Related
            "sister_concerns", "scheme_benefits", "documents",
            "required_documents", "document_verification_status",
            # Timestamps
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "is_approved", "approved_at", "created_at", "updated_at"]

    def get_required_documents(self, obj):
        return REQUIRED_DOCS_BY_TYPE.get(obj.member_type, ["aadhaar", "pan"])

    def get_document_verification_status(self, obj):
        required = REQUIRED_DOCS_BY_TYPE.get(obj.member_type, ["aadhaar", "pan"])
        uploaded = {d.document_type: d.status for d in obj.documents.all()}
        return {
            doc: uploaded.get(doc, "not_uploaded")
            for doc in required
        }


class MemberCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating member profiles."""

    sister_concerns = SisterConcernCreateSerializer(many=True, required=False)
    scheme_benefits = GovernmentSchemeBenefitCreateSerializer(many=True, required=False)

    class Meta:
        model = Member
        fields = [
            # Member type
            "member_type",
            # Personal Details
            "date_of_birth", "gender", "religion", "caste", "social_category",
            # Address
            "address_line_1", "address_line_2", "block", "district", "state", "pincode",
            # Education
            "educational_qualification", "occupation",
            # Business Details (Individual)
            "is_doing_business", "organization_name", "constitution", "business_type",
            "business_activities", "business_commencement_year", "number_of_employees",
            # Government Registrations
            "msme_registered", "msme_number", "nsic_registered", "nsic_number",
            "gst_registered", "gst_number", "ie_code",
            # Taxation
            "pan_number", "udyam_number", "has_filed_itr", "itr_filing_years",
            # Financial
            "turnover_range",
            # SHG fields
            "shg_name", "shg_registration_number", "shg_formation_date",
            "shg_member_count", "shg_bank_linked", "shg_bank_name",
            "shg_bank_account_number", "shg_promoting_institution", "shg_federation_name",
            # FPO fields
            "fpo_name", "fpo_registration_number", "fpo_registration_date",
            "fpo_farmer_count", "fpo_total_land_area_acres", "fpo_crop_types",
            "fpo_annual_turnover", "fpo_ceo_name", "fpo_ceo_phone", "fpo_commodity",
            # Other
            "member_of_other_chambers", "other_chamber_details",
            # Related
            "sister_concerns", "scheme_benefits",
        ]

    def validate(self, attrs):
        member_type = attrs.get("member_type", Member.MemberType.INDIVIDUAL)

        if member_type == Member.MemberType.SHG:
            # Validate SHG-specific format fields
            shg_reg = attrs.get("shg_registration_number", "")
            if shg_reg and len(shg_reg) < 5:
                raise serializers.ValidationError(
                    {"shg_registration_number": "Enter a valid SHG registration number."}
                )

        if member_type == Member.MemberType.FPO:
            fpo_reg = attrs.get("fpo_registration_number", "")
            if fpo_reg and len(fpo_reg) < 5:
                raise serializers.ValidationError(
                    {"fpo_registration_number": "Enter a valid FPO registration number."}
                )

        # Udyam validation (optional, format only)
        import re
        udyam = attrs.get("udyam_number", "")
        if udyam and not re.match(r"^UDYAM-[A-Z]{2}-\d{2}-\d{7}$", udyam):
            raise serializers.ValidationError(
                {"udyam_number": "Invalid Udyam number format. Expected: UDYAM-XX-00-0000000"}
            )

        # PAN validation
        pan = attrs.get("pan_number", "")
        if pan and not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", pan):
            raise serializers.ValidationError(
                {"pan_number": "Invalid PAN format. Expected: ABCDE1234F"}
            )

        # GST validation
        gst = attrs.get("gst_number", "")
        if gst and not re.match(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$", gst):
            raise serializers.ValidationError(
                {"gst_number": "Invalid GST number format."}
            )

        return attrs

    def create(self, validated_data):
        sister_concerns_data = validated_data.pop("sister_concerns", [])
        scheme_benefits_data = validated_data.pop("scheme_benefits", [])
        member = Member.objects.create(**validated_data)
        for c in sister_concerns_data:
            SisterConcern.objects.create(member=member, **c)
        for b in scheme_benefits_data:
            GovernmentSchemeBenefit.objects.create(member=member, **b)
        member.calculate_profile_completion()
        member.save()
        return member

    def update(self, instance, validated_data):
        sister_concerns_data = validated_data.pop("sister_concerns", None)
        scheme_benefits_data = validated_data.pop("scheme_benefits", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if sister_concerns_data is not None:
            instance.sister_concerns.all().delete()
            for c in sister_concerns_data:
                SisterConcern.objects.create(member=instance, **c)
        if scheme_benefits_data is not None:
            instance.scheme_benefits.all().delete()
            for b in scheme_benefits_data:
                GovernmentSchemeBenefit.objects.create(member=instance, **b)
        instance.calculate_profile_completion()
        instance.save()
        return instance


class MemberListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for member listing."""

    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    block_name = serializers.CharField(source="block.name", read_only=True, allow_null=True)
    district_name = serializers.CharField(source="district.name", read_only=True, allow_null=True)
    member_type_display = serializers.CharField(source="get_member_type_display", read_only=True)

    class Meta:
        model = Member
        fields = [
            "id", "email", "full_name",
            "member_type", "member_type_display",
            "social_category", "block_name", "district_name",
            "organization_name", "shg_name", "fpo_name",
            "profile_completion_percentage", "is_approved", "created_at",
        ]
