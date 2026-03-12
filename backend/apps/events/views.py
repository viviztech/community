"""
Views for Event Management.
"""

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Delegate, Event, EventRegistration
from .serializers import (DelegateSerializer, EventRegistrationSerializer,
                          EventSerializer)


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for events."""

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]  # Public read access

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter upcoming events
        if self.action == "list":
            queryset = queryset.filter(
                event_date__gte=timezone.now(), status="published"
            )
        return queryset.order_by("event_date")

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Get upcoming events."""
        events = self.get_queryset()
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def availability(self, request, pk=None):
        """Get ticket availability for an event."""
        event = self.get_object()
        return Response(
            {
                "available_tickets": event.available_tickets,
                "max_delegates": event.max_delegates,
                "ticket_price": event.ticket_price,
            }
        )


class EventRegistrationViewSet(viewsets.ModelViewSet):
    """ViewSet for event registrations."""

    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "member_profile"):
            return EventRegistration.objects.filter(member=user.member_profile)
        return EventRegistration.objects.none()

    def create(self, request, *args, **kwargs):
        """Create event registration with delegate details."""
        data = request.data.copy()
        data["member"] = request.user.member_profile.id

        # Get the event to calculate total
        from apps.members.models import Member
        from apps.payments.models import Payment

        try:
            event = Event.objects.get(id=data["event"])
            member = Member.objects.get(id=data["member"])
        except (Event.DoesNotExist, Member.DoesNotExist):
            return Response(
                {"error": "Invalid event or member"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate total amount
        number_of_delegates = int(data.get("number_of_delegates", 1))
        total_amount = event.ticket_price * number_of_delegates
        data["total_amount"] = total_amount

        # Create registration
        registration = EventRegistration.objects.create(
            event=event,
            member=member,
            number_of_delegates=number_of_delegates,
            total_amount=total_amount,
        )

        # Create delegates
        delegates_data = data.get("delegates", [])
        for delegate_data in delegates_data:
            Delegate.objects.create(registration=registration, **delegate_data)

        serializer = self.get_serializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def add_delegate(self, request, pk=None):
        """Add a delegate to an existing registration."""
        registration = self.get_object()
        serializer = DelegateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(registration=registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def ticket(self, request, pk=None):
        """Get ticket details."""
        registration = self.get_object()
        return Response(
            {
                "ticket_number": registration.ticket_number,
                "qr_code": registration.qr_code,
                "event": EventSerializer(registration.event).data,
                "member": registration.member.user.full_name,
                "delegates": DelegateSerializer(
                    registration.delegates.all(), many=True
                ).data,
                "total_amount": registration.total_amount,
            }
        )

    @action(detail=True, methods=["get"])
    def confirmation(self, request, pk=None):
        """Get confirmation details for ticket."""
        registration = self.get_object()
        return Response(
            {
                "message": "Your Booking is Confirmed",
                "member_name": registration.member.user.full_name,
                "event": {
                    "name": registration.event.title,
                    "date": registration.event.event_date,
                    "venue": registration.event.venue,
                    "time": registration.event.event_date,
                },
                "delegates": DelegateSerializer(
                    registration.delegates.all(), many=True
                ).data,
                "payment": {
                    "ticket_price": registration.event.ticket_price,
                    "number_of_delegates": registration.number_of_delegates,
                    "total_payment": registration.total_amount,
                },
            }
        )


class DelegateViewSet(viewsets.ModelViewSet):
    """ViewSet for delegates."""

    queryset = Delegate.objects.all()
    serializer_class = DelegateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "member_profile"):
            return Delegate.objects.filter(registration__member=user.member_profile)
        return Delegate.objects.none()
