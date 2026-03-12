"""
Serializers for Event Management.
"""

from rest_framework import serializers

from .models import Delegate, Event, EventRegistration


class EventSerializer(serializers.ModelSerializer):
    """Serializer for events."""

    available_tickets = serializers.IntegerField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "venue",
            "event_date",
            "registration_deadline",
            "ticket_price",
            "max_delegates",
            "status",
            "image",
            "organizer",
            "available_tickets",
            "is_upcoming",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "organizer", "available_tickets", "is_upcoming"]


class DelegateSerializer(serializers.ModelSerializer):
    """Serializer for delegates."""

    class Meta:
        model = Delegate
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "designation",
            "organization",
            "is_primary",
        ]
        read_only_fields = ["id"]


class EventRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for event registrations."""

    event_title = serializers.CharField(source="event.title", read_only=True)
    member_name = serializers.CharField(source="member.user.full_name", read_only=True)
    delegates = DelegateSerializer(many=True, read_only=True)

    class Meta:
        model = EventRegistration
        fields = [
            "id",
            "event",
            "event_title",
            "member",
            "member_name",
            "number_of_delegates",
            "total_amount",
            "payment_status",
            "qr_code",
            "ticket_number",
            "delegates",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "qr_code",
            "ticket_number",
            "payment_status",
            "created_at",
            "updated_at",
        ]


class EventRegistrationCreateSerializer(serializers.Serializer):
    """Serializer for creating event registrations."""

    event_id = serializers.UUIDField()
    number_of_delegates = serializers.IntegerField(min_value=1)
    delegates = DelegateSerializer(many=True)

    def validate_event_id(self, value):
        try:
            event = Event.objects.get(id=value, status="published")
            if (
                event.registration_deadline
                and event.registration_deadline < timezone.now()
            ):
                raise serializers.ValidationError("Registration deadline has passed")
        except Event.DoesNotExist:
            raise serializers.ValidationError("Invalid event")
        return value

    def validate_delegates(self, value):
        number_of_delegates = self.initial_data.get("number_of_delegates", 1)
        if len(value) != number_of_delegates:
            raise serializers.ValidationError(
                f"Expected {number_of_delegates} delegates, got {len(value)}"
            )
        return value
