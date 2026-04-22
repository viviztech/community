"""
Views for Approval Workflow.
"""

from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import AdminProfile
from apps.accounts.permissions import IsAnyAdmin

from .models import ApprovalAction, ApprovalWorkflow, EscalationRule
from .serializers import (
    ApprovalActionCreateSerializer,
    ApprovalActionSerializer,
    ApprovalWorkflowSerializer,
    EscalationRuleSerializer,
)


def _notify_member(member, subject, message):
    """Send email + SMS + push to a member, with in-app record."""
    try:
        from apps.notifications.views import NotificationService, FCMService
        NotificationService.send_email(member.user, subject, message)
        if member.user.phone_number:
            NotificationService.send_sms(member.user.phone_number, message)
        FCMService.send_push(member.user, subject, message[:200])
    except Exception as e:
        print(f"Notification error (member): {e}")


def _notify_admins_at_level(level, member, subject, message):
    """Find admins at the given level for the member's geography and notify them."""
    try:
        from apps.notifications.views import NotificationService, FCMService

        if level == ApprovalWorkflow.Level.DISTRICT:
            admins = AdminProfile.objects.filter(
                status="active", admin_level="district", area=member.district
            ).select_related("user")
        elif level == ApprovalWorkflow.Level.STATE:
            admins = AdminProfile.objects.filter(
                status="active", admin_level="state", area=member.state
            ).select_related("user")
        elif level in (ApprovalWorkflow.Level.FINAL, "final"):
            # Notify super admins and state-level admins (State Presidents)
            admins = AdminProfile.objects.filter(
                status="active", admin_level__in=["super"]
            ).select_related("user")
            state_admins = AdminProfile.objects.filter(
                status="active", admin_level="state", area=member.state
            ).select_related("user")
            for admin in state_admins:
                try:
                    NotificationService.send_email(admin.user, subject, message)
                    FCMService.send_push(admin.user, subject, message[:200])
                except Exception as e:
                    print(f"Notification error (state admin): {e}")
        else:
            admins = AdminProfile.objects.none()

        for admin in admins:
            try:
                NotificationService.send_email(admin.user, subject, message)
                FCMService.send_push(admin.user, subject, message[:200])
            except Exception as e:
                print(f"Notification error (admin {admin.user.email}): {e}")
    except Exception as e:
        print(f"Notification error (level admins): {e}")


LEVEL_LABEL = {
    ApprovalWorkflow.Level.BLOCK: "Block",
    ApprovalWorkflow.Level.DISTRICT: "District",
    ApprovalWorkflow.Level.STATE: "State",
    ApprovalWorkflow.Level.FINAL: "Final",
}


class ApprovalWorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for approval workflows."""

    queryset = ApprovalWorkflow.objects.all()
    serializer_class = ApprovalWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ApprovalWorkflow.objects.all()

        admin = getattr(user, "admin_profile", None)
        if admin and admin.status == "active":
            if admin.admin_level == "super":
                return ApprovalWorkflow.objects.all()
            if admin.admin_level == "block" and admin.area:
                return ApprovalWorkflow.objects.filter(
                    member__block=admin.area, current_level="block"
                )
            if admin.admin_level == "district" and admin.area:
                return ApprovalWorkflow.objects.filter(
                    member__district=admin.area, current_level="district"
                )
            if admin.admin_level == "state" and admin.area:
                return ApprovalWorkflow.objects.filter(
                    member__state=admin.area,
                    current_level__in=["state", "final"],
                )

        # Regular members see nothing here (use my_applications)
        return ApprovalWorkflow.objects.none()

    @action(detail=True, methods=["post"])
    def process_action(self, request, pk=None):
        """Process an approval action at the current level."""
        workflow = self.get_object()
        serializer = ApprovalActionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data["action"]
        comments = serializer.validated_data.get("comments", "")
        member = workflow.member
        current_level_label = LEVEL_LABEL.get(workflow.current_level, workflow.current_level)

        # Record the action
        action_obj = ApprovalAction.objects.create(
            workflow=workflow,
            approver=request.user,
            level=workflow.current_level,
            action=action_type,
            comments=comments,
        )

        if action_type == "approve":
            advanced = workflow.advance_to_next_level()

            if advanced:
                # Workflow moved to the next level — notify member and next-level admins
                next_level_label = LEVEL_LABEL.get(workflow.current_level, workflow.current_level)
                workflow.status = ApprovalWorkflow.Status.IN_PROGRESS
                workflow.save()

                member_msg = (
                    f"Dear {member.user.full_name},\n\n"
                    f"Your ACTIV membership application has been approved at the {current_level_label} level "
                    f"and forwarded for {next_level_label} review.\n\n"
                    f"We will keep you informed of further progress.\n\nBest regards,\nACTIV Team"
                )
                _notify_member(member, "Application Advanced to Next Level", member_msg)

                admin_msg = (
                    f"A membership application requires your review at the {next_level_label} level.\n\n"
                    f"Member: {member.user.full_name}\n"
                    f"Member Type: {member.get_member_type_display()}\n"
                    f"Block: {member.block.name if member.block else '-'}\n"
                    f"District: {member.district.name if member.district else '-'}\n"
                    f"Please log in to the admin panel to review and take action.\n\nACTIV System"
                )
                _notify_admins_at_level(workflow.current_level, member, "New Application Pending Your Review", admin_msg)

            else:
                # No next level — this is the final approval
                workflow.status = ApprovalWorkflow.Status.APPROVED
                workflow.is_active = False
                workflow.save()

                member.is_approved = True
                member.approved_at = timezone.now()
                member.save(update_fields=["is_approved", "approved_at"])

                member_msg = (
                    f"Dear {member.user.full_name},\n\n"
                    f"Congratulations! Your ACTIV membership application has been fully approved.\n\n"
                    f"You are now an approved member of ACTIV. Welcome!\n\nBest regards,\nACTIV Team"
                )
                _notify_member(member, "Membership Application Approved", member_msg)

        elif action_type == "reject":
            workflow.status = ApprovalWorkflow.Status.REJECTED
            workflow.is_active = False
            workflow.save()

            member_msg = (
                f"Dear {member.user.full_name},\n\n"
                f"We regret to inform you that your ACTIV membership application has not been approved "
                f"at the {current_level_label} level.\n\n"
                f"Reason: {comments or 'Not specified'}\n\n"
                f"Please contact us for further information or to reapply.\n\nBest regards,\nACTIV Team"
            )
            _notify_member(member, "Membership Application Not Approved", member_msg)

        elif action_type == "escalate":
            workflow.escalated_at = timezone.now()
            workflow.escalation_count += 1
            workflow.save()

            # Notify next level about the escalation
            next_level = workflow.get_next_level()
            if next_level:
                escalate_msg = (
                    f"An application has been escalated to {LEVEL_LABEL.get(next_level, next_level)} level.\n\n"
                    f"Member: {member.user.full_name}\n"
                    f"Escalated from: {current_level_label}\n"
                    f"Reason: {comments or 'Not specified'}\n\nACTIV System"
                )
                _notify_admins_at_level(next_level, member, "Application Escalated for Review", escalate_msg)

        elif action_type == "request_info":
            workflow.save()
            member_msg = (
                f"Dear {member.user.full_name},\n\n"
                f"Additional information is required for your ACTIV membership application.\n\n"
                f"Details: {comments or 'Please contact your Block Admin for details.'}\n\n"
                f"Please update your profile and resubmit.\n\nBest regards,\nACTIV Team"
            )
            _notify_member(member, "Additional Information Required", member_msg)

        return Response(
            ApprovalActionSerializer(action_obj).data, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """Get pending approvals for the current admin."""
        workflows = self.get_queryset().filter(is_active=True).exclude(status="approved")
        serializer = self.get_serializer(workflows, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_applications(self, request):
        """Get the current user's membership applications with status."""
        member = getattr(request.user, "member_profile", None)
        if not member:
            return Response([])

        workflows = ApprovalWorkflow.objects.filter(
            member=member
        ).prefetch_related("actions__approver").order_by("-created_at")

        result = []
        for wf in workflows:
            actions = []
            for act in wf.actions.all():
                actions.append({
                    "level": act.level,
                    "level_display": LEVEL_LABEL.get(act.level, act.level),
                    "action": act.action,
                    "comments": act.comments,
                    "approver_name": act.approver.full_name if act.approver else None,
                    "created_at": act.created_at,
                })
            result.append({
                "id": str(wf.id),
                "status": wf.status,
                "status_display": wf.get_status_display(),
                "current_level": wf.current_level,
                "current_level_display": LEVEL_LABEL.get(wf.current_level, wf.current_level),
                "is_active": wf.is_active,
                "created_at": wf.created_at,
                "updated_at": wf.updated_at,
                "actions": actions,
            })

        return Response(result)


class EscalationRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for escalation rules."""

    queryset = EscalationRule.objects.all()
    serializer_class = EscalationRuleSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)
