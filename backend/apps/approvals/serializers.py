"""
Serializers for Approval Workflow.
"""

from rest_framework import serializers

from .models import ApprovalAction, ApprovalWorkflow, EscalationRule


class ApprovalActionSerializer(serializers.ModelSerializer):
    """Serializer for approval actions."""

    approver_email = serializers.EmailField(source="approver.email", read_only=True)

    class Meta:
        model = ApprovalAction
        fields = [
            "id",
            "approver",
            "approver_email",
            "level",
            "action",
            "comments",
            "created_at",
        ]
        read_only_fields = ["id", "approver", "created_at"]


class ApprovalWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for approval workflows."""

    member_name = serializers.CharField(source="member.user.full_name", read_only=True)
    member_email = serializers.EmailField(source="member.user.email", read_only=True)
    actions = ApprovalActionSerializer(many=True, read_only=True)

    class Meta:
        model = ApprovalWorkflow
        fields = [
            "id",
            "member",
            "member_name",
            "member_email",
            "current_level",
            "status",
            "actions",
            "created_at",
            "updated_at",
            "escalated_at",
            "escalation_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ApprovalActionCreateSerializer(serializers.Serializer):
    """Serializer for creating approval actions."""

    action = serializers.ChoiceField(
        choices=["approve", "reject", "request_info", "escalate"]
    )
    comments = serializers.CharField(required=False, allow_blank=True)


class EscalationRuleSerializer(serializers.ModelSerializer):
    """Serializer for escalation rules."""

    level_display = serializers.CharField(source="get_level_display", read_only=True)

    class Meta:
        model = EscalationRule
        fields = [
            "id", "level", "level_display",
            "hours_to_remind", "hours_to_escalate",
            "notify_via_email", "notify_via_sms", "notify_via_whatsapp",
            "is_active",
        ]
