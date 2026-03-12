"""
Payment Models for ACTIV Membership Portal.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    """Payment model for all transactions."""

    class PaymentType(models.TextChoices):
        MEMBERSHIP_YEARLY = "membership_yearly", _("Membership - Yearly")
        MEMBERSHIP_LIFETIME = "membership_lifetime", _("Membership - Lifetime")
        EVENT_TICKET = "event_ticket", _("Event Ticket")
        DONATION = "donation", _("Donation")

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        PROCESSING = "processing", _("Processing")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")
        REFUNDED = "refunded", _("Refunded")
        CANCELLED = "cancelled", _("Cancelled")

    class PaymentGateway(models.TextChoices):
        INSTAMOJO = "instamojo", _("Instamojo")
        RAZORPAY = "razorpay", _("Razorpay")
        PAYTM = "paytm", _("Paytm")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        "members.Member", on_delete=models.CASCADE, related_name="payments"
    )
    payment_type = models.CharField(max_length=30, choices=PaymentType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="INR")
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    gateway = models.CharField(
        max_length=20, choices=PaymentGateway.choices, default=PaymentGateway.INSTAMOJO
    )
    gateway_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    gateway_payment_id = models.CharField(max_length=100, null=True, blank=True)
    receipt_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.id} - {self.amount} ({self.get_status_display()})"

    def generate_receipt(self):
        """Generate receipt number."""
        import datetime

        self.receipt_number = (
            f"RCPT/{datetime.datetime.now().year}/{self.id.hex[:8].upper()}"
        )
        self.save()
        return self.receipt_number
