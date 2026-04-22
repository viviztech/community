"""
Views for Member management.
"""

from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Q
from django.utils import timezone

from apps.accounts.permissions import IsAnyAdmin, IsBlockAdmin

from .models import GeographicArea, GovernmentSchemeBenefit, Member, MemberDocument, SisterConcern
from .serializers import (
    GeographicAreaSerializer,
    GovernmentSchemeBenefitCreateSerializer,
    MemberCreateSerializer,
    MemberDocumentSerializer,
    MemberListSerializer,
    MemberSerializer,
    SisterConcernCreateSerializer,
)


class MemberViewSet(viewsets.ModelViewSet):
    """ViewSet for member management."""

    queryset = Member.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "user__email",
        "user__first_name",
        "user__last_name",
        "organization_name",
        "block__name",
        "district__name",
    ]
    ordering_fields = ["created_at", "profile_completion_percentage"]

    def get_serializer_class(self):
        if self.action == "list":
            return MemberListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return MemberCreateSerializer
        return MemberSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.IsAuthenticated()]
        elif self.action in ["create"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        queryset = Member.objects.select_related("user", "block", "district", "state")

        # Filter by admin area using explicit AdminProfile
        admin = getattr(user, "admin_profile", None)
        if admin and admin.status == "active" and not user.is_superuser:
            if admin.admin_level == "block" and admin.area:
                queryset = queryset.filter(block=admin.area)
            elif admin.admin_level == "district" and admin.area:
                queryset = queryset.filter(district=admin.area)
            elif admin.admin_level == "state" and admin.area:
                queryset = queryset.filter(state=admin.area)

        # Apply filters from query params
        social_category = self.request.query_params.get("social_category")
        if social_category:
            queryset = queryset.filter(social_category=social_category)

        member_type = self.request.query_params.get("member_type")
        if member_type:
            queryset = queryset.filter(member_type=member_type)

        block = self.request.query_params.get("block")
        if block:
            queryset = queryset.filter(block_id=block)

        district = self.request.query_params.get("district")
        if district:
            queryset = queryset.filter(district_id=district)

        gender = self.request.query_params.get("gender")
        if gender:
            queryset = queryset.filter(gender=gender)

        return queryset

    def create(self, request, *args, **kwargs):
        """Create member profile."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            member = serializer.save(user=request.user)
            return Response(
                MemberSerializer(member).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def profile(self, request, pk=None):
        """Get full member profile."""
        member = self.get_object()
        serializer = MemberSerializer(member)
        return Response(serializer.data)

    @action(detail=False, methods=["get", "put", "patch"], url_path="my-profile")
    def my_profile(self, request):
        """Get or update current user's member profile."""
        if not request.user.is_authenticated:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            member = Member.objects.get(user=request.user)
        except Member.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.method == "GET":
            serializer = MemberSerializer(member)
            return Response(serializer.data)

        # PUT or PATCH
        serializer = MemberCreateSerializer(member, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(MemberSerializer(member).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def update_sister_concerns(self, request, pk=None):
        """Update sister concerns."""
        member = self.get_object()
        serializer = SisterConcernCreateSerializer(data=request.data, many=True)
        if serializer.is_valid():
            member.sister_concerns.all().delete()
            for concern_data in serializer.validated_data:
                SisterConcern.objects.create(member=member, **concern_data)
            return Response({"message": "Sister concerns updated."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"], url_path="required-documents")
    def required_documents(self, request):
        """Return required document types for the current user's member type."""
        from .serializers import REQUIRED_DOCS_BY_TYPE
        if not hasattr(request.user, "member_profile"):
            return Response({"error": "Member profile not found."}, status=status.HTTP_404_NOT_FOUND)
        member = request.user.member_profile
        required = REQUIRED_DOCS_BY_TYPE.get(member.member_type, ["aadhaar", "pan"])
        uploaded = {d.document_type: d.status for d in member.documents.all()}
        return Response({
            "member_type": member.member_type,
            "required_documents": required,
            "status": {doc: uploaded.get(doc, "not_uploaded") for doc in required},
        })

    @action(detail=True, methods=["post"])
    def update_scheme_benefits(self, request, pk=None):
        """Update government scheme benefits."""
        member = self.get_object()
        serializer = GovernmentSchemeBenefitCreateSerializer(
            data=request.data, many=True
        )
        if serializer.is_valid():
            member.scheme_benefits.all().delete()
            for benefit_data in serializer.validated_data:
                GovernmentSchemeBenefit.objects.create(member=member, **benefit_data)
            return Response({"message": "Scheme benefits updated."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemberDocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for member document uploads."""

    serializer_class = MemberDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return MemberDocument.objects.all()
        if hasattr(user, "member_profile"):
            return MemberDocument.objects.filter(member=user.member_profile)
        return MemberDocument.objects.none()

    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, "member_profile"):
            return Response(
                {"error": "Member profile not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        file = request.FILES.get("file")
        if not file:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        document = MemberDocument.objects.create(
            member=request.user.member_profile,
            document_type=request.data.get("document_type", "other"),
            file=file,
            original_filename=file.name,
        )
        return Response(
            MemberDocumentSerializer(document).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"], permission_classes=[IsBlockAdmin])
    def review(self, request, pk=None):
        """Admin action to approve or reject a document."""
        document = self.get_object()
        new_status = request.data.get("status")
        notes = request.data.get("notes", "")

        if new_status not in [MemberDocument.Status.VERIFIED, MemberDocument.Status.REJECTED]:
            return Response(
                {"error": "status must be 'verified' or 'rejected'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        document.status = new_status
        document.notes = notes
        document.reviewed_at = timezone.now()
        document.reviewed_by = request.user
        document.save()
        return Response(MemberDocumentSerializer(document).data)


class GeographicAreaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for geographic areas (read-only)."""

    queryset = GeographicArea.objects.all()
    serializer_class = GeographicAreaSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "code"]

    def get_queryset(self):
        queryset = GeographicArea.objects.filter(is_active=True)

        # Filter by type
        area_type = self.request.query_params.get("type")
        if area_type:
            queryset = queryset.filter(area_type=area_type)

        # Get children of parent
        parent_id = self.request.query_params.get("parent")
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)

        return queryset

    @action(detail=False, methods=["get"])
    def blocks(self, request):
        """Get all blocks."""
        blocks = GeographicArea.objects.filter(area_type="block", is_active=True)
        serializer = GeographicAreaSerializer(blocks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def districts(self, request):
        """Get all districts."""
        districts = GeographicArea.objects.filter(area_type="district", is_active=True)
        serializer = GeographicAreaSerializer(districts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def states(self, request):
        """Get all states."""
        states = GeographicArea.objects.filter(area_type="state", is_active=True)
        serializer = GeographicAreaSerializer(states, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def children(self, request, pk=None):
        """Get child areas."""
        area = self.get_object()
        children = area.children.filter(is_active=True)
        serializer = GeographicAreaSerializer(children, many=True)
        return Response(serializer.data)


class MemberDirectoryView(APIView):
    """
    Public member directory — authenticated members can browse approved members.
    Supports search, geographic filters, and social category filters.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = Member.objects.select_related(
            "user", "block", "district", "state"
        ).filter(is_approved=True, user__is_active=True)

        # Search
        search = request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(organization_name__icontains=search)
                | Q(block__name__icontains=search)
                | Q(district__name__icontains=search)
            )

        # Filters
        block_id = request.query_params.get("block")
        if block_id:
            queryset = queryset.filter(block_id=block_id)

        district_id = request.query_params.get("district")
        if district_id:
            queryset = queryset.filter(district_id=district_id)

        state_id = request.query_params.get("state")
        if state_id:
            queryset = queryset.filter(state_id=state_id)

        social_category = request.query_params.get("social_category")
        if social_category:
            queryset = queryset.filter(social_category=social_category)

        business_type = request.query_params.get("business_type")
        if business_type:
            queryset = queryset.filter(business_type=business_type)

        member_type = request.query_params.get("member_type")
        if member_type:
            queryset = queryset.filter(member_type=member_type)

        # Pagination
        page = int(request.query_params.get("page", 1))
        page_size = min(int(request.query_params.get("page_size", 20)), 100)
        start = (page - 1) * page_size
        end = start + page_size

        total = queryset.count()
        members = queryset.order_by("user__first_name")[start:end]

        return Response({
            "count": total,
            "page": page,
            "page_size": page_size,
            "results": [
                {
                    "id": m.id,
                    "name": m.user.full_name,
                    "member_type": m.member_type,
                    "member_type_display": m.get_member_type_display(),
                    "organization": m.organization_name or m.shg_name or m.fpo_name,
                    "business_type": m.business_type,
                    "constitution": m.constitution,
                    "block": m.block.name if m.block else None,
                    "district": m.district.name if m.district else None,
                    "state": m.state.name if m.state else None,
                    "social_category": m.social_category,
                    "profile_completion": m.profile_completion_percentage,
                }
                for m in members
            ],
        })


class AdminMemberApproveView(APIView):
    """
    Block/District/State admins can approve members within their area.
    This creates an ApprovalWorkflow action and advances it.
    """

    permission_classes = [IsBlockAdmin]

    def post(self, request, pk):
        try:
            member = Member.objects.select_related("user", "block", "district", "state").get(pk=pk)
        except Member.DoesNotExist:
            return Response({"error": "Member not found."}, status=status.HTTP_404_NOT_FOUND)

        admin = getattr(request.user, "admin_profile", None)
        is_super = request.user.is_superuser or (admin and admin.admin_level == "super")

        # Enforce geographic boundary
        if not is_super and admin and admin.status == "active":
            if admin.admin_level == "block" and admin.area and member.block != admin.area:
                return Response({"error": "Member is not in your block."}, status=status.HTTP_403_FORBIDDEN)
            elif admin.admin_level == "district" and admin.area and member.district != admin.area:
                return Response({"error": "Member is not in your district."}, status=status.HTTP_403_FORBIDDEN)
            elif admin.admin_level == "state" and admin.area and member.state != admin.area:
                return Response({"error": "Member is not in your state."}, status=status.HTTP_403_FORBIDDEN)

        action_type = request.data.get("action", "approve")  # approve | reject
        comments = request.data.get("comments", "")

        if action_type not in ("approve", "reject"):
            return Response({"error": "action must be 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        from apps.approvals.models import ApprovalWorkflow, ApprovalAction

        # Get or create workflow
        workflow, _ = ApprovalWorkflow.objects.get_or_create(
            member=member,
            is_active=True,
            defaults={"status": ApprovalWorkflow.Status.PENDING, "current_level": ApprovalWorkflow.Level.BLOCK},
        )

        ApprovalAction.objects.create(
            workflow=workflow,
            approver=request.user,
            level=workflow.current_level,
            action=action_type,
            comments=comments,
        )

        if action_type == "approve":
            advanced = workflow.advance_to_next_level()
            if not advanced:
                workflow.status = ApprovalWorkflow.Status.APPROVED
                workflow.is_active = False
                workflow.save()
                member.is_approved = True
                member.approved_at = timezone.now()
                member.save(update_fields=["is_approved", "approved_at"])
            else:
                workflow.status = ApprovalWorkflow.Status.IN_PROGRESS
                workflow.save()
        else:
            workflow.status = ApprovalWorkflow.Status.REJECTED
            workflow.is_active = False
            workflow.save()

        return Response({
            "message": f"Member {action_type}d successfully.",
            "workflow_status": workflow.status,
            "current_level": workflow.current_level,
            "member_approved": member.is_approved,
        })
