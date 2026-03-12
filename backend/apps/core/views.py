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
from apps.members.models import Member
from apps.memberships.models import Membership, MembershipTier
from apps.payments.models import Payment


class AdminDashboardStatsView(APIView):
    """Get admin dashboard statistics."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        stats = {}

        # Check if user is admin
        is_superadmin = user.is_superuser
        has_admin_area = hasattr(user, "member_profile") and (
            user.member_profile.block
            or user.member_profile.district
            or user.member_profile.state
        )

        if not (is_superadmin or has_admin_area):
            return Response(
                {"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN
            )

        # Base queryset based on admin level
        member_queryset = Member.objects.all()
        if not is_superadmin:
            if user.member_profile.block:
                member_queryset = member_queryset.filter(
                    block=user.member_profile.block
                )
            elif user.member_profile.district:
                member_queryset = member_queryset.filter(
                    district=user.member_profile.district
                )
            elif user.member_profile.state:
                member_queryset = member_queryset.filter(
                    state=user.member_profile.state
                )

        # Total members
        stats["total_members"] = member_queryset.count()

        # Approved members
        stats["approved_members"] = member_queryset.filter(user__is_active=True).count()

        # Pending approvals
        pending_approvals = ApprovalWorkflow.objects.filter(
            status="pending", is_active=True
        )
        if not is_superadmin:
            if user.member_profile.block:
                pending_approvals = pending_approvals.filter(
                    member__block=user.member_profile.block, current_level="block"
                )
            elif user.member_profile.district:
                pending_approvals = pending_approvals.filter(
                    member__district=user.member_profile.district,
                    current_level="district",
                )
            elif user.member_profile.state:
                pending_approvals = pending_approvals.filter(current_level="state")
        stats["pending_approvals"] = pending_approvals.count()

        # Membership tiers breakdown
        tier_stats = (
            Membership.objects.filter(status="active")
            .values("tier__name")
            .annotate(count=Count("id"))
        )
        stats["membership_tiers"] = {
            item["tier__name"]: item["count"] for item in tier_stats
        }

        # Revenue stats (this month)
        month_start = timezone.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        monthly_payments = Payment.objects.filter(
            status="completed", created_at__gte=month_start
        )
        stats["monthly_revenue"] = (
            monthly_payments.aggregate(total=Sum("amount"))["total"] or 0
        )

        # Total revenue
        stats["total_revenue"] = (
            Payment.objects.filter(status="completed").aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )

        # Events stats
        upcoming_events = Event.objects.filter(
            event_date__gt=timezone.now(), status="published"
        )
        stats["upcoming_events"] = upcoming_events.count()

        stats["total_events"] = Event.objects.count()

        # Event registrations this month
        stats["event_registrations_this_month"] = EventRegistration.objects.filter(
            created_at__gte=month_start, payment_status="completed"
        ).count()

        # Member growth (last 6 months)
        growth_data = []
        for i in range(5, -1, -1):
            month_start = timezone.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            month_start = month_start - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)

            count = Member.objects.filter(
                created_at__gte=month_start, created_at__lt=month_end
            ).count()

            growth_data.append({"month": month_start.strftime("%Y-%m"), "count": count})
        stats["member_growth"] = growth_data

        # Recent registrations
        recent_members = member_queryset.order_by("-created_at")[:5]
        stats["recent_registrations"] = [
            {
                "id": m.id,
                "name": m.user.full_name,
                "email": m.user.email,
                "organization": m.organization_name,
                "created_at": m.created_at,
            }
            for m in recent_members
        ]

        return Response(stats)


class AdminMembersListView(APIView):
    """Admin view for managing all members."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not (user.is_superuser or hasattr(user, "member_profile")):
            return Response(
                {"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN
            )

        queryset = Member.objects.select_related("user", "block", "district", "state")

        # Filter by admin area
        if not user.is_superuser:
            if user.member_profile.block:
                queryset = queryset.filter(block=user.member_profile.block)
            elif user.member_profile.district:
                queryset = queryset.filter(district=user.member_profile.district)
            elif user.member_profile.state:
                queryset = queryset.filter(state=user.member_profile.state)

        # Apply filters
        status_param = request.query_params.get("status")
        if status_param:
            if status_param == "approved":
                queryset = queryset.filter(user__is_active=True)
            elif status_param == "pending":
                queryset = queryset.filter(
                    user__is_active=True,
                    approval_workflows__status="pending",
                    approval_workflows__is_active=True,
                ).distinct()

        social_category = request.query_params.get("category")
        if social_category:
            queryset = queryset.filter(social_category=social_category)

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(organization_name__icontains=search)
            )

        # Pagination
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        start = (page - 1) * page_size
        end = start + page_size

        total = queryset.count()
        members = queryset[start:end]

        return Response(
            {
                "count": total,
                "results": [
                    {
                        "id": m.id,
                        "name": m.user.full_name,
                        "email": m.user.email,
                        "phone": (
                            str(m.user.phone_number) if m.user.phone_number else None
                        ),
                        "organization": m.organization_name,
                        "block": m.block.name if m.block else None,
                        "district": m.district.name if m.district else None,
                        "social_category": m.social_category,
                        "profile_completion": m.profile_completion_percentage,
                        "is_active": m.user.is_active,
                        "created_at": m.created_at,
                    }
                    for m in members
                ],
            }
        )


class AdminApprovalsListView(APIView):
    """Admin view for managing approvals."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not (user.is_superuser or hasattr(user, "member_profile")):
            return Response(
                {"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN
            )

        queryset = ApprovalWorkflow.objects.select_related(
            "member", "member__user"
        ).filter(is_active=True)

        # Filter by admin level
        if not user.is_superuser:
            if user.member_profile.block:
                queryset = queryset.filter(
                    member__block=user.member_profile.block, current_level="block"
                )
            elif user.member_profile.district:
                queryset = queryset.filter(
                    member__district=user.member_profile.district,
                    current_level="district",
                )
            elif user.member_profile.state:
                queryset = queryset.filter(current_level="state")

        # Filter by status
        status_param = request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Pagination
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        start = (page - 1) * page_size
        end = start + page_size

        total = queryset.count()
        workflows = queryset[start:end]

        return Response(
            {
                "count": total,
                "results": [
                    {
                        "id": w.id,
                        "member_name": w.member.user.full_name,
                        "member_email": w.member.user.email,
                        "member_organization": w.member.organization_name,
                        "current_level": w.current_level,
                        "status": w.status,
                        "created_at": w.created_at,
                        "escalation_count": w.escalation_count,
                    }
                    for w in workflows
                ],
            }
        )


class AdminRevenueStatsView(APIView):
    """Get revenue statistics."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_superuser:
            return Response(
                {"error": "Super admin access required"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Revenue by payment type
        revenue_by_type = (
            Payment.objects.filter(status="completed")
            .values("payment_type")
            .annotate(total=Sum("amount"), count=Count("id"))
        )

        # Revenue by month (last 12 months)
        monthly_revenue = []
        for i in range(11, -1, -1):
            month_start = timezone.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            if i > 0:
                month_start = (month_start - timedelta(days=1)).replace(day=1)
            month_end = month_start + timedelta(days=32)
            month_end = month_end.replace(day=1)

            total = (
                Payment.objects.filter(
                    status="completed",
                    created_at__gte=month_start,
                    created_at__lt=month_end,
                ).aggregate(total=Sum("amount"))["total"]
                or 0
            )

            monthly_revenue.append(
                {"month": month_start.strftime("%Y-%m"), "total": float(total)}
            )

        return Response(
            {
                "total_revenue": Payment.objects.filter(status="completed").aggregate(
                    total=Sum("amount")
                )["total"]
                or 0,
                "total_transactions": Payment.objects.filter(
                    status="completed"
                ).count(),
                "revenue_by_type": {
                    item["payment_type"]: {
                        "total": float(item["total"]),
                        "count": item["count"],
                    }
                    for item in revenue_by_type
                },
                "monthly_revenue": monthly_revenue,
            }
        )


class AdminGeographicStatsView(APIView):
    """Get geographic distribution statistics."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not (user.is_superuser or hasattr(user, "member_profile")):
            return Response(
                {"error": "Admin access required"}, status=status.HTTP_403_FORBIDDEN
            )

        queryset = Member.objects.filter(user__is_active=True)

        if not user.is_superuser:
            if user.member_profile.state:
                queryset = queryset.filter(state=user.member_profile.state)
            elif user.member_profile.district:
                queryset = queryset.filter(district=user.member_profile.district)

        # Members by district
        by_district = (
            queryset.values("district__name")
            .annotate(count=Count("id"))
            .exclude(district__name__isnull=True)
        )

        # Members by block
        by_block = (
            queryset.values("block__name")
            .annotate(count=Count("id"))
            .exclude(block__name__isnull=True)
        )

        # Members by social category
        by_category = (
            queryset.values("social_category")
            .annotate(count=Count("id"))
            .exclude(social_category__isnull=True)
        )

        return Response(
            {
                "by_district": [
                    {"name": item["district__name"], "count": item["count"]}
                    for item in by_district
                ],
                "by_block": [
                    {"name": item["block__name"], "count": item["count"]}
                    for item in by_block
                ],
                "by_social_category": [
                    {"category": item["social_category"], "count": item["count"]}
                    for item in by_category
                ],
            }
        )
