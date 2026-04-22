from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminMemberApproveView, GeographicAreaViewSet, MemberDirectoryView, MemberDocumentViewSet, MemberViewSet

router = DefaultRouter()
router.register(r"", MemberViewSet, basename="member")
router.register(r"areas", GeographicAreaViewSet, basename="area")
router.register(r"documents", MemberDocumentViewSet, basename="member-document")

urlpatterns = [
    path("directory/", MemberDirectoryView.as_view(), name="member-directory"),
    path("<uuid:pk>/approve/", AdminMemberApproveView.as_view(), name="member-approve"),
    path("", include(router.urls)),
]
