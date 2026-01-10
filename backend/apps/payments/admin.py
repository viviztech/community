from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'member', 'amount', 'payment_type', 'status', 'gateway', 'created_at')
    list_filter = ('payment_type', 'status', 'gateway')
    raw_id_fields = ('member',)
    readonly_fields = ('created_at', 'updated_at')
