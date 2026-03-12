from django.http import HttpResponse
from django.urls import path

from .views import (AdminApprovalsListView, AdminDashboardStatsView,
                    AdminGeographicStatsView, AdminMembersListView,
                    AdminRevenueStatsView)


def health_check(request):
    return HttpResponse("OK")


urlpatterns = [
    path("health/", health_check, name="health-check"),
    # Admin Dashboard APIs
    path(
        "admin/dashboard/stats/",
        AdminDashboardStatsView.as_view(),
        name="admin-dashboard-stats",
    ),
    path("admin/members/", AdminMembersListView.as_view(), name="admin-members-list"),
    path(
        "admin/approvals/",
        AdminApprovalsListView.as_view(),
        name="admin-approvals-list",
    ),
    path("admin/revenue/", AdminRevenueStatsView.as_view(), name="admin-revenue-stats"),
    path(
        "admin/geographic-stats/",
        AdminGeographicStatsView.as_view(),
        name="admin-geographic-stats",
    ),
]
