"""
Celery tasks for Approval Workflow automation.

Schedule (all SLAs are 24 h per level, reminder at 12 h):
  - check_approval_reminders_and_escalations  — runs every hour
"""

from celery import shared_task
from django.utils import timezone

LEVEL_LABEL = {
    "block": "Block",
    "district": "District",
    "state": "State",
    "final": "Final",
}

NEXT_LEVEL = {
    "block": "district",
    "district": "state",
    "state": "final",
    "final": None,
}


def _get_admins_at_level(level, member):
    """Return active AdminProfile queryset for the given level + geography."""
    from apps.accounts.models import AdminProfile

    if level == "block":
        return AdminProfile.objects.filter(
            status="active", admin_level="block", area=member.block
        ).select_related("user")
    if level == "district":
        return AdminProfile.objects.filter(
            status="active", admin_level="district", area=member.district
        ).select_related("user")
    if level in ("state", "final"):
        return AdminProfile.objects.filter(
            status="active", admin_level__in=["state", "super"]
        ).select_related("user")
    return []


def _notify_user(user, subject, body):
    """Email + SMS + push to a single user — all failures are silenced."""
    try:
        from apps.notifications.views import NotificationService
        NotificationService.send_email(user, subject, body)
    except Exception as e:
        print(f"[notify] email error for {user.email}: {e}")

    try:
        if user.phone_number:
            from apps.notifications.views import NotificationService
            NotificationService.send_sms(str(user.phone_number), body[:160])
    except Exception as e:
        print(f"[notify] sms error for {user.email}: {e}")

    try:
        from apps.notifications.views import FCMService
        FCMService.send_push(user, subject, body[:200])
    except Exception as e:
        print(f"[notify] push error for {user.email}: {e}")


@shared_task(bind=True, max_retries=3)
def check_approval_reminders_and_escalations(self):
    """
    Runs every hour. For each active workflow:
      - At 12 h: send reminder to admins at current level
      - At 24 h: auto-escalate to next level (or mark overdue for final)
    """
    from .models import ApprovalWorkflow, EscalationRule

    now = timezone.now()
    processed = {"reminded": 0, "escalated": 0}

    # Build a rule map keyed by level
    rules = {r.level: r for r in EscalationRule.objects.filter(is_active=True)}

    active_workflows = ApprovalWorkflow.objects.filter(
        is_active=True,
        status__in=["pending", "in_progress"],
    ).select_related("member", "member__user", "member__block", "member__district", "member__state")

    for workflow in active_workflows:
        rule = rules.get(workflow.current_level)
        if not rule:
            continue

        hours_waiting = (now - workflow.level_entered_at).total_seconds() / 3600
        member = workflow.member
        level_label = LEVEL_LABEL.get(workflow.current_level, workflow.current_level)

        # ── REMINDER (12 h) ────────────────────────────────────────────────
        if hours_waiting >= rule.hours_to_remind and workflow.reminder_sent_at is None:
            subject = f"[ACTIV] Action Required: Membership Application Pending ({level_label} Level)"
            body = (
                f"This is a reminder that a membership application has been waiting for your review "
                f"at the {level_label} level for more than {rule.hours_to_remind} hours.\n\n"
                f"Member: {member.user.full_name}\n"
                f"Member Type: {member.get_member_type_display()}\n"
                f"Block: {member.block.name if member.block else '-'}\n"
                f"District: {member.district.name if member.district else '-'}\n\n"
                f"Please log in to the admin panel and take action.\n\n"
                f"This application will be auto-escalated if not acted upon within "
                f"{rule.hours_to_escalate - rule.hours_to_remind} more hours.\n\nACTIV System"
            )
            for admin in _get_admins_at_level(workflow.current_level, member):
                _notify_user(admin.user, subject, body)

            workflow.reminder_sent_at = now
            workflow.save(update_fields=["reminder_sent_at"])
            processed["reminded"] += 1

        # ── ESCALATION (24 h) ───────────────────────────────────────────────
        if hours_waiting >= rule.hours_to_escalate:
            next_level = NEXT_LEVEL.get(workflow.current_level)

            if next_level:
                # Advance the workflow
                old_level = workflow.current_level
                old_label = LEVEL_LABEL.get(old_level, old_level)
                workflow.current_level = next_level
                workflow.level_entered_at = now
                workflow.reminder_sent_at = None
                workflow.escalated_at = now
                workflow.escalation_count = (workflow.escalation_count or 0) + 1
                workflow.status = "in_progress"
                workflow.save()

                # Notify member
                member_body = (
                    f"Dear {member.user.full_name},\n\n"
                    f"Your ACTIV membership application was not reviewed within the expected time at the "
                    f"{old_label} level and has been automatically escalated to the "
                    f"{LEVEL_LABEL.get(next_level, next_level)} level for review.\n\n"
                    f"We will notify you of further progress.\n\nBest regards,\nACTIV Team"
                )
                _notify_user(
                    member.user,
                    f"Application Auto-Escalated to {LEVEL_LABEL.get(next_level, next_level)} Level",
                    member_body,
                )

                # Notify next-level admins
                next_label = LEVEL_LABEL.get(next_level, next_level)
                admin_body = (
                    f"A membership application has been auto-escalated to your level ({next_label}) "
                    f"due to inactivity at the {old_label} level.\n\n"
                    f"Member: {member.user.full_name}\n"
                    f"Member Type: {member.get_member_type_display()}\n"
                    f"Block: {member.block.name if member.block else '-'}\n"
                    f"District: {member.district.name if member.district else '-'}\n\n"
                    f"Please review and take action promptly.\n\nACTIV System"
                )
                for admin in _get_admins_at_level(next_level, member):
                    _notify_user(
                        admin.user,
                        f"[ACTIV] Escalated Application — {next_label} Review Required",
                        admin_body,
                    )

            else:
                # Already at final level and overdue — ping super admins
                subject = "[ACTIV] URGENT: Final Approval Overdue"
                body = (
                    f"The following membership application has been waiting at the Final level "
                    f"for more than {rule.hours_to_escalate} hours and requires immediate action.\n\n"
                    f"Member: {member.user.full_name}\n"
                    f"Member Type: {member.get_member_type_display()}\n"
                    f"Waiting: {hours_waiting:.0f} hours\n\n"
                    f"Please log in and approve or reject.\n\nACTIV System"
                )
                for admin in _get_admins_at_level("final", member):
                    _notify_user(admin.user, subject, body)

                # Bump escalation count so we don't spam every hour
                workflow.escalation_count = (workflow.escalation_count or 0) + 1
                workflow.escalated_at = now
                # Reset level_entered_at by 12h so next ping is 12h later, not immediately
                workflow.level_entered_at = now - timezone.timedelta(hours=rule.hours_to_remind)
                workflow.save(update_fields=["escalation_count", "escalated_at", "level_entered_at"])

            processed["escalated"] += 1

    return (
        f"Reminders sent: {processed['reminded']} | "
        f"Escalations: {processed['escalated']}"
    )


@shared_task
def seed_default_escalation_rules():
    """
    Idempotent task to ensure default EscalationRule rows exist.
    Safe to call multiple times. Also used by the management command.
    """
    from .models import ApprovalWorkflow, EscalationRule

    defaults = [
        {"level": "block",    "hours_to_remind": 12, "hours_to_escalate": 24, "escalate_to": "district"},
        {"level": "district", "hours_to_remind": 12, "hours_to_escalate": 24, "escalate_to": "state"},
        {"level": "state",    "hours_to_remind": 12, "hours_to_escalate": 24, "escalate_to": "final"},
        {"level": "final",    "hours_to_remind": 12, "hours_to_escalate": 24, "escalate_to": ""},
    ]

    created = 0
    for row in defaults:
        _, was_created = EscalationRule.objects.update_or_create(
            level=row["level"],
            defaults={
                "hours_to_remind": row["hours_to_remind"],
                "hours_to_escalate": row["hours_to_escalate"],
                "escalate_to": row["escalate_to"],
                "notify_via_email": True,
                "notify_via_sms": True,
                "notify_via_whatsapp": True,
                "is_active": True,
            },
        )
        if was_created:
            created += 1

    return f"EscalationRule rows ensured: {created} created"
