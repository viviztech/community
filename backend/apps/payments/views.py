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
        """Handle Instamojo webhook callback with signature verification."""
        import hashlib
        import hmac

        # Verify Instamojo HMAC signature
        salt = settings.INSTAMOJO_SALT
        if salt:
            mac_provided = request.data.get("mac", "")
            data_for_mac = "|".join([
                str(request.data.get("payment_id", "")),
                str(request.data.get("payment_request_id", "")),
                str(request.data.get("buyer", "")),
                str(request.data.get("buyer_name", "")),
                str(request.data.get("buyer_phone", "")),
                str(request.data.get("amount", "")),
                str(request.data.get("fees", "")),
                str(request.data.get("currency", "")),
                str(request.data.get("status", "")),
                str(request.data.get("longurl", "")),
                str(request.data.get("purpose", "")),
            ])
            expected_mac = hmac.new(
                salt.encode("utf-8"), data_for_mac.encode("utf-8"), hashlib.sha1
            ).hexdigest()

            if not hmac.compare_digest(mac_provided, expected_mac):
                return Response({"error": "Invalid signature"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        try:
            payment = Payment.objects.get(gateway_transaction_id=data.get("payment_request_id"))
        except Payment.DoesNotExist:
            return Response({"status": "ignored"}, status=200)

        # Update payment status
        payment_status = data.get("status", "").lower()
        if payment_status == "credit":
            payment.status = "completed"
            payment.gateway_payment_id = data.get("payment_id")
            payment.generate_receipt()
            payment.save()

            # Trigger post-payment actions
            self.handle_payment_completed(payment)

            # Send payment confirmation notification
            try:
                from apps.notifications.views import NotificationService
                NotificationService.send_email(
                    payment.member.user,
                    "Payment Confirmed - ACTIV",
                    f"Dear {payment.member.user.full_name},\n\nYour payment of ₹{payment.amount} has been received successfully.\n\nReceipt No: {payment.receipt_number}\nTransaction ID: {payment.gateway_payment_id}\n\nThank you!\nACTIV Team",
                )
            except Exception:
                pass

        return Response({"status": "received"})

    @action(detail=True, methods=["get"])
    def receipt(self, request, pk=None):
        """Get payment receipt as JSON or PDF."""
        payment = self.get_object()

        if request.query_params.get("format") == "pdf":
            return self._generate_receipt_pdf(payment)

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

    def _generate_receipt_pdf(self, payment):
        """Generate a PDF payment receipt."""
        from io import BytesIO

        from django.http import HttpResponse
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.pdfgen import canvas

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Header
        c.setFillColor(colors.HexColor("#1a1a2e"))
        c.rect(0, height - 4*cm, width, 4*cm, fill=True, stroke=False)

        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor("#f0a500"))
        c.drawString(2*cm, height - 2*cm, "ACTIV")

        c.setFont("Helvetica", 10)
        c.setFillColor(colors.white)
        c.drawString(2*cm, height - 2.8*cm, "Adidravidar Confederation of Trade and Industrial Vision")

        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.white)
        c.drawRightString(width - 2*cm, height - 2*cm, "PAYMENT RECEIPT")

        # Receipt details
        y = height - 6*cm
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.black)

        details = [
            ("Receipt No:", payment.receipt_number or "N/A"),
            ("Member Name:", payment.member.user.full_name),
            ("Email:", payment.member.user.email),
            ("Payment Type:", payment.get_payment_type_display()),
            ("Amount:", f"Rs. {payment.amount}"),
            ("Transaction ID:", payment.gateway_payment_id or payment.gateway_transaction_id or "N/A"),
            ("Date:", payment.created_at.strftime("%d %B %Y %I:%M %p") if payment.created_at else "N/A"),
            ("Status:", payment.status.upper()),
        ]

        for label, value in details:
            c.setFont("Helvetica-Bold", 11)
            c.drawString(2*cm, y, label)
            c.setFont("Helvetica", 11)
            c.drawString(8*cm, y, str(value))
            y -= 0.8*cm

        # Footer
        c.setStrokeColor(colors.HexColor("#cccccc"))
        c.line(2*cm, 4*cm, width - 2*cm, 4*cm)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.grey)
        c.drawCentredString(width / 2, 3*cm, "This is a computer-generated receipt. No signature required.")
        c.drawCentredString(width / 2, 2.4*cm, "ACTIV - activ.org.in")

        c.save()
        buffer.seek(0)

        response = HttpResponse(buffer.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="receipt_{payment.receipt_number or payment.id}.pdf"'
        return response

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
        from django.shortcuts import redirect as django_redirect

        payment_request_id = request.query_params.get("payment_request_id")
        payment_id = request.query_params.get("payment_id")
        payment_status = request.query_params.get("payment_status", "").lower()

        frontend_url = settings.FRONTEND_URL

        try:
            payment = Payment.objects.get(gateway_transaction_id=payment_request_id)

            if payment_status == "credit":
                if payment.status != "completed":
                    payment.status = "completed"
                    payment.gateway_payment_id = payment_id
                    payment.generate_receipt()
                    payment.save()
                    PaymentViewSet().handle_payment_completed(payment)

                return django_redirect(f"{frontend_url}/payments/success?payment_id={payment.id}")

            payment.status = "failed"
            payment.save()
            return django_redirect(f"{frontend_url}/payments/failed")

        except Payment.DoesNotExist:
            return django_redirect(f"{frontend_url}/payments/failed")
