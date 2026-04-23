"""
Views for Admin Dashboard.
"""

from datetime import timedelta

from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.approvals.models import ApprovalWorkflow
from apps.events.models import Event, EventRegistration
from apps.members.models import GeographicArea, Member
from apps.memberships.models import Membership, MembershipTier
from apps.payments.models import Payment


def _admin_member_queryset(user, base_qs=None):
    """Return Member queryset scoped to the admin's geographic area."""
    if base_qs is None:
        base_qs = Member.objects.all()
    if user.is_superuser:
        return base_qs
    admin = getattr(user, "admin_profile", None)
    if admin and admin.status == "active":
        if admin.admin_level in ("super",):
            return base_qs
        if admin.admin_level == "state" and admin.area:
            return base_qs.filter(state=admin.area)
        if admin.admin_level == "district" and admin.area:
            return base_qs.filter(district=admin.area)
        if admin.admin_level == "block" and admin.area:
            return base_qs.filter(block=admin.area)
    return base_qs.none()


def _apply_common_filters(queryset, params):
    """Apply area (block/district) and gender filters from query params."""
    block_id = params.get("block")
    if block_id:
        queryset = queryset.filter(block_id=block_id)

    district_id = params.get("district")
    if district_id:
        queryset = queryset.filter(district_id=district_id)

    gender = params.get("gender")
    if gender:
        queryset = queryset.filter(gender=gender)

    member_type = params.get("member_type")
    if member_type:
        queryset = queryset.filter(member_type=member_type)

    social_category = params.get("social_category")
    if social_category:
        queryset = queryset.filter(social_category=social_category)

    return queryset


class AdminDashboardStatsView(APIView):
    """
    Role-specific dashboard statistics.
    Block admin  → block-scoped metrics
    District admin → district-scoped metrics + block breakdown
    State admin  → state-scoped metrics + district breakdown
    Super admin  → all-India metrics + state breakdown
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        admin_profile = getattr(user, "admin_profile", None)
        is_superadmin = user.is_superuser or (admin_profile and admin_profile.admin_level == "super")
        is_any_admin = user.is_superuser or (admin_profile and admin_profile.status == "active")

        if not is_any_admin:
            return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)

        admin_level = "super" if is_superadmin else (admin_profile.admin_level if admin_profile else "super")

        # Base member queryset (geo-scoped)
        base_qs = _admin_member_queryset(user, Member.objects.select_related("user", "block", "district", "state"))
        params = request.query_params
        filtered_qs = _apply_common_filters(base_qs, params)

        # ── Core counts ──────────────────────────────────────────────────────
        total_members = filtered_qs.count()
        approved_members = filtered_qs.filter(is_approved=True).count()
        pending_members = filtered_qs.filter(is_approved=False).count()

        # Gender breakdown
        gender_breakdown = {
            "male": filtered_qs.filter(gender="M").count(),
            "female": filtered_qs.filter(gender="F").count(),
            "other": filtered_qs.filter(gender="O").count(),
            "not_set": filtered_qs.filter(gender__isnull=True).count(),
        }

        # Member type breakdown
        type_breakdown = {
            row["member_type"]: row["count"]
            for row in filtered_qs.values("member_type").annotate(count=Count("id"))
        }

        # Social category breakdown
        category_breakdown = {
            row["social_category"]: row["count"]
            for row in filtered_qs.exclude(social_category__isnull=True)
                                  .values("social_category").annotate(count=Count("id"))
        }

        # ── Pending approvals (level-specific) ───────────────────────────────
        approval_qs = ApprovalWorkflow.objects.filter(is_active=True)
        if not is_superadmin and admin_profile and admin_profile.status == "active":
            if admin_profile.admin_level == "block" and admin_profile.area:
                approval_qs = approval_qs.filter(member__block=admin_profile.area, current_level="block")
            elif admin_profile.admin_level == "district" and admin_profile.area:
                approval_qs = approval_qs.filter(member__district=admin_profile.area, current_level="district")
            elif admin_profile.admin_level == "state" and admin_profile.area:
                approval_qs = approval_qs.filter(current_level__in=["state", "final"])

        # Apply geo filters to approvals too
        if params.get("block"):
            approval_qs = approval_qs.filter(member__block_id=params["block"])
        if params.get("district"):
            approval_qs = approval_qs.filter(member__district_id=params["district"])
        if params.get("gender"):
            approval_qs = approval_qs.filter(member__gender=params["gender"])

        pending_approvals = approval_qs.filter(status__in=["pending", "in_progress"]).count()
        # SLA breach: pending for > 24 h at current level
        sla_threshold = timezone.now() - timedelta(hours=24)
        sla_breached = approval_qs.filter(
            status__in=["pending", "in_progress"],
            level_entered_at__lte=sla_threshold,
        ).count()

        # ── Area breakdown (role-specific) ───────────────────────────────────
        if admin_level in ("super", "state"):
            # Show breakdown by district
            area_breakdown = [
                {"name": row["district__name"], "count": row["count"]}
                for row in filtered_qs.exclude(district__isnull=True)
                                      .values("district__name").annotate(count=Count("id"))
                                      .order_by("-count")
            ]
            area_label = "By District"
        elif admin_level == "district":
            # Show breakdown by block
            area_breakdown = [
                {"name": row["block__name"], "count": row["count"]}
                for row in filtered_qs.exclude(block__isnull=True)
                                      .values("block__name").annotate(count=Count("id"))
                                      .order_by("-count")
            ]
            area_label = "By Block"
        else:
            # Block admin — no further breakdown
            area_breakdown = []
            area_label = ""

        # ── Member growth (last 6 months) ────────────────────────────────────
        growth_data = []
        now = timezone.now()
        for i in range(5, -1, -1):
            m_start = (now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                       - timedelta(days=30 * i))
            m_end = m_start + timedelta(days=32)
            m_end = m_end.replace(day=1)
            count = filtered_qs.filter(created_at__gte=m_start, created_at__lt=m_end).count()
            growth_data.append({"month": m_start.strftime("%b %Y"), "count": count})

        # ── Revenue (super/state only) ───────────────────────────────────────
        monthly_revenue = 0
        total_revenue = 0
        if admin_level in ("super", "state") and not params.get("block") and not params.get("district"):
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_revenue = float(
                Payment.objects.filter(status="completed", created_at__gte=month_start)
                               .aggregate(t=Sum("amount"))["t"] or 0
            )
            total_revenue = float(
                Payment.objects.filter(status="completed").aggregate(t=Sum("amount"))["t"] or 0
            )

        # ── Events (super/state/district) ────────────────────────────────────
        upcoming_events = 0
        if admin_level in ("super", "state", "district"):
            upcoming_events = Event.objects.filter(
                event_date__gt=now, status="published"
            ).count()

        # ── Recent registrations ─────────────────────────────────────────────
        recent = filtered_qs.order_by("-created_at")[:5]
        recent_registrations = [
            {
                "id": str(m.id),
                "name": m.user.full_name,
                "email": m.user.email,
                "member_type": m.member_type,
                "block": m.block.name if m.block else None,
                "district": m.district.name if m.district else None,
                "gender": m.gender,
                "is_approved": m.is_approved,
                "created_at": m.created_at,
            }
            for m in recent
        ]

        return Response({
            "admin_level": admin_level,
            "admin_area": admin_profile.area.name if (admin_profile and admin_profile.area) else None,
            # Core
            "total_members": total_members,
            "approved_members": approved_members,
            "pending_members": pending_members,
            "pending_approvals": pending_approvals,
            "sla_breached": sla_breached,
            # Breakdowns
            "gender_breakdown": gender_breakdown,
            "type_breakdown": type_breakdown,
            "category_breakdown": category_breakdown,
            "area_breakdown": area_breakdown,
            "area_label": area_label,
            # Charts
            "member_growth": growth_data,
            # Finance (super/state)
            "monthly_revenue": monthly_revenue,
            "total_revenue": total_revenue,
            # Events
            "upcoming_events": upcoming_events,
            # Recent
            "recent_registrations": recent_registrations,
        })


class AdminMembersListView(APIView):
    """Admin view for members with area, gender, type filters."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        admin_profile = getattr(user, "admin_profile", None)
        is_any_admin = user.is_superuser or (admin_profile and admin_profile.status == "active")
        if not is_any_admin:
            return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)

        queryset = _admin_member_queryset(
            user, Member.objects.select_related("user", "block", "district", "state")
        )
        queryset = _apply_common_filters(queryset, request.query_params)

        # Approval status filter
        approval_status = request.query_params.get("approval_status")
        if approval_status == "approved":
            queryset = queryset.filter(is_approved=True)
        elif approval_status == "pending":
            queryset = queryset.filter(is_approved=False)

        # Free-text search
        search = request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(organization_name__icontains=search)
                | Q(shg_name__icontains=search)
                | Q(fpo_name__icontains=search)
            )

        # Pagination
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        start = (page - 1) * page_size

        total = queryset.count()
        members = queryset.order_by("-created_at")[start: start + page_size]

        return Response({
            "count": total,
            "results": [
                {
                    "id": str(m.id),
                    "name": m.user.full_name,
                    "email": m.user.email,
                    "phone": str(m.user.phone_number) if m.user.phone_number else None,
                    "member_type": m.member_type,
                    "member_type_display": m.get_member_type_display(),
                    "organization": m.organization_name or m.shg_name or m.fpo_name,
                    "block": m.block.name if m.block else None,
                    "block_id": str(m.block_id) if m.block_id else None,
                    "district": m.district.name if m.district else None,
                    "district_id": str(m.district_id) if m.district_id else None,
                    "gender": m.gender,
                    "social_category": m.social_category,
                    "profile_completion": m.profile_completion_percentage,
                    "is_approved": m.is_approved,
                    "created_at": m.created_at,
                }
                for m in members
            ],
        })


class AdminApprovalsListView(APIView):
    """Admin view for approval queue with area and gender filters."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        admin_profile = getattr(user, "admin_profile", None)
        is_any_admin = user.is_superuser or (admin_profile and admin_profile.status == "active")
        if not is_any_admin:
            return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)

        queryset = ApprovalWorkflow.objects.select_related(
            "member", "member__user", "member__block", "member__district"
        ).filter(is_active=True)

        # Scope to admin level
        if not user.is_superuser and admin_profile and admin_profile.status == "active":
            if admin_profile.admin_level == "block" and admin_profile.area:
                queryset = queryset.filter(member__block=admin_profile.area, current_level="block")
            elif admin_profile.admin_level == "district" and admin_profile.area:
                queryset = queryset.filter(member__district=admin_profile.area, current_level="district")
            elif admin_profile.admin_level == "state" and admin_profile.area:
                queryset = queryset.filter(current_level__in=["state", "final"])

        # Filters
        if request.query_params.get("block"):
            queryset = queryset.filter(member__block_id=request.query_params["block"])
        if request.query_params.get("district"):
            queryset = queryset.filter(member__district_id=request.query_params["district"])
        if request.query_params.get("gender"):
            queryset = queryset.filter(member__gender=request.query_params["gender"])
        if request.query_params.get("member_type"):
            queryset = queryset.filter(member__member_type=request.query_params["member_type"])

        wf_status = request.query_params.get("status", "active")
        if wf_status == "active":
            queryset = queryset.filter(status__in=["pending", "in_progress"])
        elif wf_status in ("approved", "rejected", "pending", "in_progress"):
            queryset = queryset.filter(status=wf_status)

        search = request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(member__user__first_name__icontains=search)
                | Q(member__user__last_name__icontains=search)
                | Q(member__user__email__icontains=search)
            )

        # Pagination
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        start = (page - 1) * page_size

        total = queryset.count()
        workflows = queryset.order_by("level_entered_at")[start: start + page_size]

        now = timezone.now()
        sla_threshold = now - timedelta(hours=24)
        remind_threshold = now - timedelta(hours=12)

        return Response({
            "count": total,
            "results": [
                {
                    "id": str(w.id),
                    "member_name": w.member.user.full_name,
                    "member_email": w.member.user.email,
                    "member_type": w.member.member_type,
                    "member_type_display": w.member.get_member_type_display(),
                    "member_organization": w.member.organization_name or w.member.shg_name or w.member.fpo_name,
                    "member_gender": w.member.gender,
                    "block": w.member.block.name if w.member.block else None,
                    "district": w.member.district.name if w.member.district else None,
                    "current_level": w.current_level,
                    "status": w.status,
                    "escalation_count": w.escalation_count,
                    "level_entered_at": w.level_entered_at,
                    "hours_waiting": round((now - w.level_entered_at).total_seconds() / 3600, 1),
                    "sla_breached": w.level_entered_at <= sla_threshold,
                    "reminder_due": w.level_entered_at <= remind_threshold and w.reminder_sent_at is None,
                    "created_at": w.created_at,
                }
                for w in workflows
            ],
        })


class AdminGeographicStatsView(APIView):
    """Geographic distribution stats with filter support."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        admin_profile = getattr(user, "admin_profile", None)
        is_any_admin = user.is_superuser or (admin_profile and admin_profile.status == "active")
        if not is_any_admin:
            return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)

        queryset = _admin_member_queryset(user, Member.objects.all())
        queryset = _apply_common_filters(queryset, request.query_params)

        by_district = [
            {"name": r["district__name"], "count": r["count"]}
            for r in queryset.exclude(district__isnull=True)
                             .values("district__name").annotate(count=Count("id")).order_by("-count")
        ]
        by_block = [
            {"name": r["block__name"], "count": r["count"]}
            for r in queryset.exclude(block__isnull=True)
                             .values("block__name").annotate(count=Count("id")).order_by("-count")
        ]
        by_social_category = [
            {"category": r["social_category"], "count": r["count"]}
            for r in queryset.exclude(social_category__isnull=True)
                             .values("social_category").annotate(count=Count("id"))
        ]
        by_gender = [
            {"gender": r["gender"] or "Not set", "count": r["count"]}
            for r in queryset.values("gender").annotate(count=Count("id"))
        ]
        by_member_type = [
            {"type": r["member_type"], "count": r["count"]}
            for r in queryset.values("member_type").annotate(count=Count("id"))
        ]

        return Response({
            "by_district": by_district,
            "by_block": by_block,
            "by_social_category": by_social_category,
            "by_gender": by_gender,
            "by_member_type": by_member_type,
        })


class AdminRevenueStatsView(APIView):
    """Revenue stats — super/state admin only."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        admin_profile = getattr(user, "admin_profile", None)
        is_finance_admin = user.is_superuser or (
            admin_profile and admin_profile.status == "active"
            and admin_profile.admin_level in ("super", "state")
        )
        if not is_finance_admin:
            return Response({"error": "State/Super admin access required"}, status=status.HTTP_403_FORBIDDEN)

        revenue_by_type = (
            Payment.objects.filter(status="completed")
            .values("payment_type").annotate(total=Sum("amount"), count=Count("id"))
        )

        monthly_revenue = []
        now = timezone.now()
        for i in range(11, -1, -1):
            m_start = (now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                       - timedelta(days=30 * i))
            m_end = (m_start + timedelta(days=32)).replace(day=1)
            total = float(
                Payment.objects.filter(
                    status="completed", created_at__gte=m_start, created_at__lt=m_end
                ).aggregate(t=Sum("amount"))["t"] or 0
            )
            monthly_revenue.append({"month": m_start.strftime("%b %Y"), "total": total})

        return Response({
            "total_revenue": float(
                Payment.objects.filter(status="completed").aggregate(t=Sum("amount"))["t"] or 0
            ),
            "total_transactions": Payment.objects.filter(status="completed").count(),
            "revenue_by_type": {
                item["payment_type"]: {"total": float(item["total"]), "count": item["count"]}
                for item in revenue_by_type
            },
            "monthly_revenue": monthly_revenue,
        })


class AdminAreaListView(APIView):
    """
    Returns blocks and districts visible to this admin —
    used to populate the filter dropdowns in the dashboard.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        admin_profile = getattr(user, "admin_profile", None)
        is_any_admin = user.is_superuser or (admin_profile and admin_profile.status == "active")
        if not is_any_admin:
            return Response({"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN)

        blocks_qs = GeographicArea.objects.filter(area_type="block", is_active=True)
        districts_qs = GeographicArea.objects.filter(area_type="district", is_active=True)

        # Scope to admin area
        if not user.is_superuser and admin_profile and admin_profile.status == "active":
            if admin_profile.admin_level == "district" and admin_profile.area:
                blocks_qs = blocks_qs.filter(parent=admin_profile.area)
                districts_qs = districts_qs.filter(id=admin_profile.area_id)
            elif admin_profile.admin_level == "block" and admin_profile.area:
                blocks_qs = blocks_qs.filter(id=admin_profile.area_id)
                districts_qs = districts_qs.filter(id=admin_profile.area.parent_id) if admin_profile.area.parent else districts_qs.none()

        return Response({
            "blocks": [{"id": str(a.id), "name": a.name} for a in blocks_qs.order_by("name")],
            "districts": [{"id": str(a.id), "name": a.name} for a in districts_qs.order_by("name")],
        })
