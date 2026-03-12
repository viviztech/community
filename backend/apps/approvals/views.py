"""
Views for Approval Workflow.
"""

from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ApprovalAction, ApprovalWorkflow, EscalationRule
from .serializers import (
    ApprovalActionCreateSerializer,
    ApprovalActionSerializer,
    ApprovalWorkflowSerializer,
    EscalationRuleSerializer,
)


class ApprovalWorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for approval workflows."""

    queryset = ApprovalWorkflow.objects.all()
    serializer_class = ApprovalWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ApprovalWorkflow.objects.all()
        # Filter by admin's area of responsibility
        if hasattr(user, "member_profile"):
            member = user.member_profile
            if member.block:
                return ApprovalWorkflow.objects.filter(
                    member__block=member.block, current_level="block"
                )
            if member.district:
                return ApprovalWorkflow.objects.filter(
                    member__district=member.district, current_level="district"
                )
            if member.state:
                return ApprovalWorkflow.objects.filter(current_level="state")
        return ApprovalWorkflow.objects.none()

    @action(detail=True, methods=["post"])
    def process_action(self, request, pk=None):
        """Process an approval action (approve/reject/request_info/escalate)."""
        workflow = self.get_object()
        serializer = ApprovalActionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data["action"]
        comments = serializer.validated_data.get("comments", "")

        # Create the action
        action_obj = ApprovalAction.objects.create(
            workflow=workflow,
            approver=request.user,
            level=workflow.current_level,
            action=action_type,
            comments=comments,
        )

        if action_type == "approve":
            next_level = workflow.advance_to_next_level()
            if not next_level:
                # Final approval
                workflow.status = "approved"
                workflow.is_active = False

                # Activate member's membership
                from apps.members.models import Member

                try:
                    member = workflow.member
                    member.is_approved = True
                    member.save()
                except Member.DoesNotExist:
                    pass

            workflow.save()

        elif action_type == "reject":
            workflow.status = "rejected"
            workflow.is_active = False
            workflow.save()

        elif action_type == "escalate":
            workflow.escalated_at = timezone.now()
            workflow.escalation_count += 1
            workflow.save()

        return Response(
            ApprovalActionSerializer(action_obj).data, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """Get pending approvals for the current user."""
        workflows = self.get_queryset().filter(status="pending", is_active=True)
        serializer = self.get_serializer(workflows, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_applications(self, request):
        """Get the current user's membership applications."""
        if not hasattr(request.user, "member_profile"):
            return Response([])

        workflows = ApprovalWorkflow.objects.filter(
            member=request.user.member_profile
        ).order_by("-created_at")

        serializer = self.get_serializer(workflows, many=True)
        return Response(serializer.data)


class EscalationRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for escalation rules."""

    queryset = EscalationRule.objects.all()
    serializer_class = EscalationRuleSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
