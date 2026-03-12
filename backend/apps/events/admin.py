from django.contrib import admin

from .models import Delegate, Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "venue", "event_date", "ticket_price", "status")
    list_filter = ("status",)
    raw_id_fields = ("organizer",)


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "member",
        "number_of_delegates",
        "total_amount",
        "payment_status",
    )
    list_filter = ("payment_status",)
    raw_id_fields = ("event", "member", "payment")


@admin.register(Delegate)
class DelegateAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "designation", "organization")
    search_fields = ("name", "email", "phone")
    raw_id_fields = ("registration",)
