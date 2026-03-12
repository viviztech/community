"""
Views for Payment Processing.
"""

import json
import uuid

import requests
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for payments."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "member_profile"):
            return Payment.objects.filter(member=user.member_profile)
        return Payment.objects.none()

    @action(detail=False, methods=["post"])
    def initiate(self, request):
        """Initiate a payment with Instamojo."""
        from apps.members.models import Member

        data = request.data
        try:
            member = Member.objects.get(id=data["member_id"])
        except Member.DoesNotExist:
            return Response(
                {"error": "Invalid member"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create payment record
        payment = Payment.objects.create(
            member=member,
            payment_type=data["payment_type"],
            amount=data["amount"],
            description=data.get("description", ""),
        )

        # Call Instamojo API to create payment request
        instamojo_response = self.create_instamojo_request(payment)

        if instamojo_response:
            payment.gateway_transaction_id = instamojo_response.get("id")
            payment.save()

            return Response(
                {
                    "payment_id": str(payment.id),
                    "payment_url": instamojo_response.get("longurl"),
                }
            )

        return Response(
            {"error": "Failed to create payment request"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["post"])
    def webhook(self, request):
        """Handle Instamojo webhook callback."""
        data = request.data

        try:
            payment = Payment.objects.get(gateway_transaction_id=data.get("payment_id"))
        except Payment.DoesNotExist:
            return Response({"status": "ignored"}, status=200)

        # Update payment status
        payment_status = data.get("status", "").lower()
        if payment_status == "completed":
            payment.status = "completed"
            payment.gateway_payment_id = data.get("payment_id")
            payment.generate_receipt()
            payment.save()

            # Trigger post-payment actions
            self.handle_payment_completed(payment)

        return Response({"status": "received"})

    @action(detail=True, methods=["get"])
    def receipt(self, request, pk=None):
        """Get payment receipt."""
        payment = self.get_object()
        return Response(
            {
                "receipt_number": payment.receipt_number,
                "member_name": payment.member.user.full_name,
                "amount": payment.amount,
                "payment_type": payment.get_payment_type_display(),
                "date": payment.created_at,
                "transaction_id": payment.gateway_transaction_id,
            }
        )

    def create_instamojo_request(self, payment):
        """Create a payment request on Instamojo."""
        api_key = settings.INSTAMOJO_API_KEY
        auth_token = settings.INSTAMOJO_AUTH_TOKEN
        endpoint = settings.INSTAMOJO_ENDPOINT

        payload = {
            "purpose": payment.description or "Payment",
            "amount": str(payment.amount),
            "buyer_name": payment.member.user.full_name,
            "email": payment.member.user.email,
            "phone": (
                str(payment.member.user.phone_number)
                if payment.member.user.phone_number
                else ""
            ),
            "redirect_url": f"{settings.SITE_URL}/payments/callback/",
            "webhook_url": f"{settings.SITE_URL}/api/v1/payments/webhook/",
        }

        headers = {
            "X-Api-Key": api_key,
            "X-Auth-Token": auth_token,
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                f"{endpoint}v2/payment_requests/",
                data=json.dumps(payload),
                headers=headers,
                timeout=30,
            )

            if response.status_code == 201:
                return response.json().get("payment_request")
        except Exception as e:
            print(f"Instamojo API error: {e}")

        return None

    def handle_payment_completed(self, payment):
        """Handle post-payment actions."""
        from apps.events.models import EventRegistration
        from apps.memberships.models import Membership

        if payment.payment_type == "membership_yearly":
            # Activate yearly membership
            try:
                membership = Membership.objects.get(payment=payment)
                membership.status = "active"
                membership.save()
            except Membership.DoesNotExist:
                pass

        elif payment.payment_type == "membership_lifetime":
            # Activate lifetime membership
            try:
                membership = Membership.objects.get(payment=payment)
                membership.status = "active"
                membership.membership_type = "lifetime"
                membership.end_date = None
                membership.save()
            except Membership.DoesNotExist:
                pass

        elif payment.payment_type == "event_ticket":
            # Confirm event registration
            try:
                registration = EventRegistration.objects.get(payment=payment)
                registration.payment_status = "completed"
                registration.generate_ticket()
                registration.save()
            except EventRegistration.DoesNotExist:
                pass


class InstamojoCallbackView(APIView):
    """Handle Instamojo payment callback."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Handle successful payment redirect."""
        payment_id = request.query_params.get("payment_id")
        status_param = request.query_params.get("status")

        try:
            payment = Payment.objects.get(gateway_transaction_id=payment_id)

            if status_param == "completed":
                payment.status = "completed"
                payment.save()
                # Redirect to success page
                return Response({"status": "success", "payment_id": str(payment.id)})

            return Response({"status": "failed"})

        except Payment.DoesNotExist:
            return Response({"status": "invalid"})
