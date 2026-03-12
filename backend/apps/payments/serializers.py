"""
Serializers for Payment Processing.
"""

from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""

    member_name = serializers.CharField(source="member.user.full_name", read_only=True)
    member_email = serializers.EmailField(source="member.user.email", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "member",
            "member_name",
            "member_email",
            "payment_type",
            "amount",
            "currency",
            "status",
            "gateway",
            "gateway_transaction_id",
            "gateway_payment_id",
            "receipt_number",
            "description",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "gateway_transaction_id",
            "gateway_payment_id",
            "receipt_number",
            "created_at",
            "updated_at",
        ]


class PaymentInitiateSerializer(serializers.Serializer):
    """Serializer for initiating a payment."""

    member_id = serializers.UUIDField()
    payment_type = serializers.ChoiceField(choices=Payment.PaymentType.choices)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)


class PaymentCallbackSerializer(serializers.Serializer):
    """Serializer for payment callback data."""

    payment_id = serializers.CharField()
    status = serializers.CharField()
