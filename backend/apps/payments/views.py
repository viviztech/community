"""
Views for Payment Processing — Instamojo integration.
"""

import hashlib
import hmac
import json
import uuid as uuid_module
from io import BytesIO

import requests
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .serializers import PaymentSerializer


# ─── helpers ──────────────────────────────────────────────────────────────────

def _create_instamojo_request(payment):
    """Create a payment request on Instamojo v2 and return the payment_request dict."""
    api_key = getattr(settings, "INSTAMOJO_API_KEY", "")
    auth_token = getattr(settings, "INSTAMOJO_AUTH_TOKEN", "")
    endpoint = getattr(settings, "INSTAMOJO_ENDPOINT", "https://www.instamojo.com/")
    site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")

    payload = {
        "purpose": (payment.description or payment.get_payment_type_display())[:30],
        "amount": str(payment.amount),
        "buyer_name": payment.member.user.full_name,
        "email": payment.member.user.email,
        "phone": str(payment.member.user.phone_number) if payment.member.user.phone_number else "",
        "redirect_url": f"{site_url}/api/v1/payments/callback/",
        "webhook": f"{site_url}/api/v1/payments/webhook/",
        "allow_repeated_payments": False,
        "send_email": True,
        "send_sms": bool(payment.member.user.phone_number),
    }

    headers = {
        "X-Api-Key": api_key,
        "X-Auth-Token": auth_token,
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            f"{endpoint.rstrip('/')}/v2/payment_requests/",
            data=json.dumps(payload),
            headers=headers,
            timeout=30,
        )
        if resp.status_code == 201:
            return resp.json().get("payment_request")
        print(f"Instamojo error {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Instamojo API error: {e}")
    return None


def _verify_webhook_mac(data):
    """Verify Instamojo HMAC-SHA1 signature. Returns True if valid or salt not configured."""
    salt = getattr(settings, "INSTAMOJO_SALT", "")
    if not salt:
        return True
    mac_provided = data.get("mac", "")
    # Field order per Instamojo docs
    fields = [
        str(data.get("payment_id", "")),
        str(data.get("payment_request_id", "")),
        str(data.get("buyer", "")),
        str(data.get("buyer_name", "")),
        str(data.get("buyer_phone", "")),
        str(data.get("amount", "")),
        str(data.get("fees", "")),
        str(data.get("currency", "")),
        str(data.get("status", "")),
        str(data.get("longurl", "")),
        str(data.get("purpose", "")),
    ]
    data_str = "|".join(fields)
    expected = hmac.new(
        salt.encode("utf-8"), data_str.encode("utf-8"), hashlib.sha1
    ).hexdigest()
    return hmac.compare_digest(mac_provided, expected)


def _handle_payment_completed(payment):
    """Activate membership / event registration after successful payment."""
    from apps.memberships.models import Membership

    if payment.payment_type in ("membership_yearly", "membership_lifetime"):
        try:
            membership = Membership.objects.get(payment=payment)
            membership.status = "active"
            if payment.payment_type == "membership_lifetime":
                membership.membership_type = "lifetime"
                membership.end_date = None
            if not membership.certificate_number:
                membership.generate_certificate()
            membership.save()
        except Membership.DoesNotExist:
            pass

    elif payment.payment_type == "event_ticket":
        try:
            from apps.events.models import EventRegistration
            reg = EventRegistration.objects.get(payment=payment)
            reg.payment_status = "completed"
            if hasattr(reg, "generate_ticket"):
                reg.generate_ticket()
            reg.save()
        except Exception:
            pass


def _send_receipt_and_certificate_email(payment):
    """Email the member a receipt PDF and (if membership) a certificate PDF."""
    try:
        from apps.notifications.views import NotificationService

        member = payment.member
        receipt_pdf = _build_receipt_pdf(payment)

        attachments = [
            (f"receipt_{payment.receipt_number}.pdf", receipt_pdf, "application/pdf"),
        ]

        # Also attach certificate for membership payments
        if payment.payment_type in ("membership_yearly", "membership_lifetime"):
            try:
                from apps.memberships.models import Membership
                membership = Membership.objects.get(payment=payment)
                if not membership.certificate_number:
                    membership.generate_certificate()
                    membership.save()
                cert_pdf = _build_certificate_pdf(membership)
                attachments.append(
                    (f"membership_certificate_{membership.certificate_number}.pdf", cert_pdf, "application/pdf")
                )
            except Exception as e:
                print(f"Certificate attach error: {e}")

        body = (
            f"Dear {member.user.full_name},\n\n"
            f"Thank you for your payment. Your transaction has been completed successfully.\n\n"
            f"Receipt No    : {payment.receipt_number}\n"
            f"Amount        : ₹{payment.amount}\n"
            f"Payment Type  : {payment.get_payment_type_display()}\n"
            f"Transaction ID: {payment.gateway_payment_id or 'N/A'}\n"
            f"Date          : {payment.created_at.strftime('%d %B %Y %I:%M %p IST')}\n\n"
            f"Your receipt is attached. You can also download it anytime from your member portal.\n\n"
            f"Thank you for being a valued ACTIV member.\n\nBest regards,\nACTIV Team"
        )

        NotificationService.send_email(
            member.user,
            f"Payment Receipt — ACTIV (₹{payment.amount})",
            body,
            attachments=attachments,
        )
    except Exception as e:
        print(f"Receipt email error: {e}")


# ─── PDF builders ─────────────────────────────────────────────────────────────

def _build_receipt_pdf(payment):
    """Return receipt PDF as bytes."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ── Header bar ──
    c.setFillColor(colors.HexColor("#1a237e"))
    c.rect(0, height - 4 * cm, width, 4 * cm, fill=True, stroke=False)

    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(colors.HexColor("#ffd600"))
    c.drawString(2 * cm, height - 1.8 * cm, "ACTIV")

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.white)
    c.drawString(2 * cm, height - 2.6 * cm, "Adidravidar Confederation of Trade and Industrial Vision")

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.white)
    c.drawRightString(width - 2 * cm, height - 1.8 * cm, "PAYMENT RECEIPT")

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#bbdefb"))
    c.drawRightString(width - 2 * cm, height - 2.6 * cm, f"Receipt No: {payment.receipt_number or 'PENDING'}")

    # ── Divider line ──
    y = height - 5 * cm
    c.setStrokeColor(colors.HexColor("#e3e3e3"))
    c.setLineWidth(0.5)
    c.line(2 * cm, y, width - 2 * cm, y)
    y -= 0.6 * cm

    # ── Member info box ──
    c.setFillColor(colors.HexColor("#f5f5f5"))
    c.roundRect(2 * cm, y - 3.2 * cm, width - 4 * cm, 3.2 * cm, 0.3 * cm, fill=True, stroke=False)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1a237e"))
    c.drawString(2.5 * cm, y - 0.7 * cm, "BILLED TO")

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.black)
    c.drawString(2.5 * cm, y - 1.4 * cm, payment.member.user.full_name)

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#555555"))
    c.drawString(2.5 * cm, y - 2 * cm, payment.member.user.email)
    phone = str(payment.member.user.phone_number) if payment.member.user.phone_number else ""
    if phone:
        c.drawString(2.5 * cm, y - 2.6 * cm, phone)

    y -= 4 * cm

    # ── Payment details table ──
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#1a237e"))
    c.drawString(2 * cm, y, "PAYMENT DETAILS")
    y -= 0.5 * cm
    c.setStrokeColor(colors.HexColor("#1a237e"))
    c.setLineWidth(1.5)
    c.line(2 * cm, y, width - 2 * cm, y)
    y -= 0.6 * cm

    rows = [
        ("Payment Type", payment.get_payment_type_display()),
        ("Member ID", str(payment.member.id)[:8].upper()),
        ("Member Type", payment.member.get_member_type_display()),
        ("Transaction ID", payment.gateway_payment_id or payment.gateway_transaction_id or "N/A"),
        ("Gateway", "Instamojo"),
        ("Date & Time", payment.created_at.strftime("%d %B %Y  %I:%M %p IST") if payment.created_at else "N/A"),
        ("Status", payment.get_status_display()),
    ]

    for label, value in rows:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(2 * cm, y, label)
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        c.drawString(9 * cm, y, str(value))
        y -= 0.7 * cm

    y -= 0.4 * cm

    # ── Amount box ──
    c.setFillColor(colors.HexColor("#1a237e"))
    c.roundRect(width - 7 * cm, y - 1.5 * cm, 5 * cm, 1.5 * cm, 0.3 * cm, fill=True, stroke=False)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.white)
    c.drawCentredString(width - 4.5 * cm, y - 0.5 * cm, "AMOUNT PAID")
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#ffd600"))
    c.drawCentredString(width - 4.5 * cm, y - 1.1 * cm, f"₹{payment.amount:,.2f}")

    # ── Footer ──
    c.setStrokeColor(colors.HexColor("#cccccc"))
    c.setLineWidth(0.5)
    c.line(2 * cm, 3.5 * cm, width - 2 * cm, 3.5 * cm)

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#777777"))
    c.drawCentredString(width / 2, 3 * cm, "This is a computer-generated receipt and does not require a signature.")
    c.drawCentredString(width / 2, 2.5 * cm, "ACTIV — Adidravidar Confederation of Trade and Industrial Vision")
    c.drawCentredString(width / 2, 2 * cm, "activ.org.in  |  For queries contact: info@activ.org.in")

    c.save()
    buffer.seek(0)
    return buffer.read()


def _build_certificate_pdf(membership):
    """Return membership certificate PDF as bytes."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    width, height = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # ── Dark background ──
    c.setFillColor(colors.HexColor("#0d1b2a"))
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # ── Gold border (outer + inner) ──
    c.setStrokeColor(colors.HexColor("#ffd600"))
    c.setLineWidth(4)
    c.rect(1 * cm, 1 * cm, width - 2 * cm, height - 2 * cm, fill=False, stroke=True)
    c.setLineWidth(1)
    c.rect(1.3 * cm, 1.3 * cm, width - 2.6 * cm, height - 2.6 * cm, fill=False, stroke=True)

    # ── Header ──
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(colors.HexColor("#ffd600"))
    c.drawCentredString(width / 2, height - 3.5 * cm, "ACTIV")

    c.setFont("Helvetica", 13)
    c.setFillColor(colors.HexColor("#bbdefb"))
    c.drawCentredString(width / 2, height - 4.5 * cm, "Adidravidar Confederation of Trade and Industrial Vision")

    # ── Decorative line ──
    c.setStrokeColor(colors.HexColor("#ffd600"))
    c.setLineWidth(1)
    c.line(width / 2 - 8 * cm, height - 5 * cm, width / 2 + 8 * cm, height - 5 * cm)

    # ── Certificate title ──
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(colors.white)
    c.drawCentredString(width / 2, height - 6.5 * cm, "Certificate of Membership")

    # ── Body ──
    c.setFont("Helvetica", 13)
    c.setFillColor(colors.HexColor("#cfd8dc"))
    c.drawCentredString(width / 2, height - 8 * cm, "This is to certify that")

    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.HexColor("#ffd600"))
    c.drawCentredString(width / 2, height - 9.2 * cm, membership.member.user.full_name)

    # Underline name
    name_width = c.stringWidth(membership.member.user.full_name, "Helvetica-Bold", 24)
    c.setStrokeColor(colors.HexColor("#ffd600"))
    c.setLineWidth(0.8)
    c.line(width / 2 - name_width / 2, height - 9.5 * cm, width / 2 + name_width / 2, height - 9.5 * cm)

    # Member details lines
    member = membership.member
    org = member.organization_name or member.shg_name or member.fpo_name or ""
    org_line = f"of {org}" if org else ""

    c.setFont("Helvetica", 13)
    c.setFillColor(colors.HexColor("#cfd8dc"))
    c.drawCentredString(width / 2, height - 10.5 * cm,
        f"is a registered {member.get_member_type_display()} member of ACTIV {org_line}")

    c.drawCentredString(width / 2, height - 11.3 * cm,
        f"under the  {membership.tier.name}  membership tier")

    start = membership.start_date.strftime("%d %B %Y")
    end = membership.end_date.strftime("%d %B %Y") if membership.end_date else "Lifetime"
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.white)
    c.drawCentredString(width / 2, height - 12.2 * cm, f"Valid From: {start}    To: {end}")

    # ── Membership type badge ──
    badge_label = "LIFETIME MEMBER" if membership.membership_type == "lifetime" else "ANNUAL MEMBER"
    c.setFillColor(colors.HexColor("#1a237e"))
    c.roundRect(width / 2 - 3.5 * cm, height - 13.5 * cm, 7 * cm, 0.9 * cm, 0.2 * cm, fill=True, stroke=False)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.HexColor("#ffd600"))
    c.drawCentredString(width / 2, height - 13 * cm, badge_label)

    # ── Footer row ──
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#90a4ae"))
    c.drawString(2 * cm, 2.2 * cm, f"Certificate No: {membership.certificate_number}")
    c.drawCentredString(width / 2, 2.2 * cm, "activ.org.in")
    c.drawRightString(width - 2 * cm, 2.2 * cm,
        f"Issued: {membership.certificate_issued_at.strftime('%d %B %Y') if membership.certificate_issued_at else ''}")

    c.save()
    buffer.seek(0)
    return buffer.read()


# ─── ViewSet ──────────────────────────────────────────────────────────────────

class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for payments."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Payment.objects.all()
        member = getattr(user, "member_profile", None)
        if member:
            return Payment.objects.filter(member=member)
        return Payment.objects.none()

    # ── POST /payments/initiate/ ──────────────────────────────────────────────
    @action(detail=False, methods=["post"])
    def initiate(self, request):
        """
        Initiate a payment with Instamojo.

        Body:
          payment_type  — membership_yearly | membership_lifetime | donation
          tier_id       — required for membership types
          amount        — required for donation
          description   — optional
          membership_id — if renewing an existing membership
        """
        from datetime import timedelta

        from apps.members.models import Member

        member = getattr(request.user, "member_profile", None)
        if not member:
            return Response({"error": "Member profile not found"}, status=status.HTTP_400_BAD_REQUEST)

        payment_type = request.data.get("payment_type")
        valid_types = [c[0] for c in Payment.PaymentType.choices]
        if payment_type not in valid_types:
            return Response({"error": f"Invalid payment_type. Choose from: {valid_types}"}, status=status.HTTP_400_BAD_REQUEST)

        # ── Determine amount ──
        if payment_type in ("membership_yearly", "membership_lifetime"):
            from apps.memberships.models import Membership, MembershipTier

            tier_id = request.data.get("tier_id")
            if not tier_id:
                return Response({"error": "tier_id required for membership payments"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                tier = MembershipTier.objects.get(id=tier_id, is_active=True)
            except MembershipTier.DoesNotExist:
                return Response({"error": "Invalid or inactive tier"}, status=status.HTTP_400_BAD_REQUEST)

            amount = tier.yearly_price if payment_type == "membership_yearly" else tier.lifetime_price
            if not amount:
                return Response({"error": f"No {payment_type} price configured for this tier"}, status=status.HTTP_400_BAD_REQUEST)

            description = f"ACTIV {tier.name} {tier.get_tier_type_display() if hasattr(tier, 'get_tier_type_display') else ''} — {'Yearly' if payment_type == 'membership_yearly' else 'Lifetime'} Membership"

            # Create or reuse pending Membership
            membership_id = request.data.get("membership_id")
            if membership_id:
                try:
                    membership = Membership.objects.get(id=membership_id, member=member)
                    membership.tier = tier
                    membership.membership_type = "yearly" if payment_type == "membership_yearly" else "lifetime"
                    membership.save()
                except Membership.DoesNotExist:
                    membership = None
            else:
                membership = None

            if not membership:
                start_date = timezone.now().date()
                end_date = start_date + timedelta(days=365) if payment_type == "membership_yearly" else None
                membership = Membership.objects.create(
                    member=member,
                    tier=tier,
                    membership_type="yearly" if payment_type == "membership_yearly" else "lifetime",
                    start_date=start_date,
                    end_date=end_date,
                    status="pending",
                )

        elif payment_type == "donation":
            amount = request.data.get("amount")
            if not amount:
                return Response({"error": "amount required for donations"}, status=status.HTTP_400_BAD_REQUEST)
            description = request.data.get("description", "Donation to ACTIV")
            membership = None

        else:
            amount = request.data.get("amount")
            description = request.data.get("description", payment_type)
            membership = None

        # ── Create Payment record ──
        payment = Payment.objects.create(
            member=member,
            payment_type=payment_type,
            amount=amount,
            description=description,
            gateway=Payment.PaymentGateway.INSTAMOJO,
        )

        # Link membership → payment
        if membership:
            membership.payment = payment
            membership.save(update_fields=["payment"])

        # ── Call Instamojo ──
        instamojo_resp = _create_instamojo_request(payment)
        if instamojo_resp:
            payment.gateway_transaction_id = instamojo_resp.get("id")
            payment.save(update_fields=["gateway_transaction_id"])
            return Response({
                "payment_id": str(payment.id),
                "payment_url": instamojo_resp.get("longurl"),
                "membership_id": str(membership.id) if membership else None,
            })

        # Instamojo unavailable — clean up
        payment.delete()
        if membership and not membership_id:
            membership.delete()
        return Response({"error": "Failed to create Instamojo payment request. Please try again."}, status=status.HTTP_502_BAD_GATEWAY)

    # ── POST /payments/webhook/ ───────────────────────────────────────────────
    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def webhook(self, request):
        """Instamojo webhook — verifies HMAC signature and activates membership."""
        if not _verify_webhook_mac(request.data):
            return Response({"error": "Invalid signature"}, status=status.HTTP_403_FORBIDDEN)

        payment_request_id = request.data.get("payment_request_id")
        try:
            payment = Payment.objects.get(gateway_transaction_id=payment_request_id)
        except Payment.DoesNotExist:
            return Response({"status": "ignored"})

        if payment.status == Payment.PaymentStatus.COMPLETED:
            return Response({"status": "already_processed"})

        instamojo_status = request.data.get("status", "").lower()
        payment.gateway_payment_id = request.data.get("payment_id")

        if instamojo_status == "credit":
            payment.status = Payment.PaymentStatus.COMPLETED
            payment.generate_receipt()
            payment.save()
            _handle_payment_completed(payment)
            _send_receipt_and_certificate_email(payment)
        else:
            payment.status = Payment.PaymentStatus.FAILED
            payment.save()

        return Response({"status": "received"})

    # ── GET /payments/{id}/receipt/ ───────────────────────────────────────────
    @action(detail=True, methods=["get"])
    def receipt(self, request, pk=None):
        """Download receipt as PDF or get JSON metadata."""
        payment = self.get_object()

        if not payment.receipt_number:
            return Response({"error": "Receipt not yet generated. Payment may still be pending."}, status=status.HTTP_400_BAD_REQUEST)

        fmt = request.query_params.get("format", "json")
        if fmt == "pdf":
            pdf_bytes = _build_receipt_pdf(payment)
            resp = HttpResponse(pdf_bytes, content_type="application/pdf")
            resp["Content-Disposition"] = f'attachment; filename="ACTIV_Receipt_{payment.receipt_number}.pdf"'
            return resp

        return Response({
            "receipt_number": payment.receipt_number,
            "member_name": payment.member.user.full_name,
            "member_email": payment.member.user.email,
            "payment_type": payment.get_payment_type_display(),
            "amount": str(payment.amount),
            "currency": payment.currency,
            "transaction_id": payment.gateway_payment_id or payment.gateway_transaction_id,
            "date": payment.created_at,
            "status": payment.status,
        })

    # ── POST /payments/donate/ ────────────────────────────────────────────────
    @action(detail=False, methods=["post"])
    def donate(self, request):
        """Shortcut endpoint for donations."""
        amount = request.data.get("amount")
        if not amount:
            return Response({"error": "amount is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            float(amount)
        except (ValueError, TypeError):
            return Response({"error": "amount must be a number"}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "payment_type": "donation",
            "amount": amount,
            "description": request.data.get("description", "Donation to ACTIV"),
        }
        request._full_data = data
        return self.initiate(request)


# ─── Certificate download view ────────────────────────────────────────────────

class MembershipCertificateView(APIView):
    """GET /payments/memberships/{membership_id}/certificate/ — download PDF certificate."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, membership_id):
        from apps.memberships.models import Membership

        member = getattr(request.user, "member_profile", None)
        try:
            qs = Membership.objects.select_related("member", "member__user", "tier")
            if request.user.is_staff or request.user.is_superuser:
                membership = qs.get(id=membership_id)
            else:
                if not member:
                    return Response({"error": "Member profile not found"}, status=status.HTTP_403_FORBIDDEN)
                membership = qs.get(id=membership_id, member=member)
        except Membership.DoesNotExist:
            return Response({"error": "Membership not found"}, status=status.HTTP_404_NOT_FOUND)

        if membership.status != "active":
            return Response({"error": "Certificate is only available for active memberships."}, status=status.HTTP_400_BAD_REQUEST)

        if not membership.certificate_number:
            membership.generate_certificate()

        pdf_bytes = _build_certificate_pdf(membership)
        resp = HttpResponse(pdf_bytes, content_type="application/pdf")
        resp["Content-Disposition"] = (
            f'attachment; filename="ACTIV_Certificate_{membership.certificate_number}.pdf"'
        )
        return resp


# ─── Callback view ────────────────────────────────────────────────────────────

class InstamojoCallbackView(APIView):
    """
    Instamojo redirect_url handler.
    Instamojo GETs this after the user completes payment on their page.
    We finalise the payment and redirect the browser to the frontend.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        from django.shortcuts import redirect

        payment_request_id = request.query_params.get("payment_request_id")
        payment_id = request.query_params.get("payment_id")
        payment_status = request.query_params.get("payment_status", "").lower()
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")

        try:
            payment = Payment.objects.select_related("member", "member__user").get(
                gateway_transaction_id=payment_request_id
            )
        except Payment.DoesNotExist:
            return redirect(f"{frontend_url}/payments/failed")

        if payment.status == Payment.PaymentStatus.COMPLETED:
            # Already processed by webhook — just redirect to success
            return redirect(f"{frontend_url}/payments/success?payment_id={payment.id}")

        if payment_status == "credit":
            payment.status = Payment.PaymentStatus.COMPLETED
            payment.gateway_payment_id = payment_id
            payment.generate_receipt()
            payment.save()
            _handle_payment_completed(payment)
            _send_receipt_and_certificate_email(payment)
            return redirect(f"{frontend_url}/payments/success?payment_id={payment.id}")

        payment.status = Payment.PaymentStatus.FAILED
        payment.save()
        return redirect(f"{frontend_url}/payments/failed")
