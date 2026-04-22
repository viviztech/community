"""
Management command: seed default EscalationRule rows.
Run once after deployment (idempotent — safe to re-run).

  python manage.py seed_escalation_rules
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed default EscalationRule rows (24 h SLA, 12 h reminder) for all approval levels."

    def handle(self, *args, **options):
        from apps.approvals.models import EscalationRule

        defaults = [
            {"level": "block",    "hours_to_remind": 12, "hours_to_escalate": 24, "escalate_to": "district"},
            {"level": "district", "hours_to_remind": 12, "hours_to_escalate": 24, "escalate_to": "state"},
            {"level": "state",    "hours_to_remind": 12, "hours_to_escalate": 24, "escalate_to": "final"},
            {"level": "final",    "hours_to_remind": 12, "hours_to_escalate": 24, "escalate_to": ""},
        ]

        for row in defaults:
            obj, created = EscalationRule.objects.update_or_create(
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
            status = "created" if created else "updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"  [{status}] {obj.get_level_display()} — "
                    f"remind at {obj.hours_to_remind}h, escalate at {obj.hours_to_escalate}h"
                )
            )

        self.stdout.write(self.style.SUCCESS("\nEscalation rules seeded successfully."))
