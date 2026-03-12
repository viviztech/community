"""
Views for Member management.
"""

from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import GeographicArea, GovernmentSchemeBenefit, Member, SisterConcern
from .serializers import (
    GeographicAreaSerializer,
    GovernmentSchemeBenefitCreateSerializer,
    MemberCreateSerializer,
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

        # Filter by admin area
        if hasattr(user, "admin_profile"):
            admin = user.admin_profile
            if admin.admin_level == "block":
                queryset = queryset.filter(block=admin.area)
            elif admin.admin_level == "district":
                queryset = queryset.filter(district=admin.area)
            elif admin.admin_level == "state":
                queryset = queryset.filter(state=admin.area)

        # Apply filters from query params
        social_category = self.request.query_params.get("social_category")
        if social_category:
            queryset = queryset.filter(social_category=social_category)

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
