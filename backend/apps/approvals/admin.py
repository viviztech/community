from django.contrib import admin
from .models import ApprovalWorkflow, ApprovalAction, EscalationRule


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ('member', 'current_level', 'status', 'is_active', 'created_at')
    list_filter = ('current_level', 'status', 'is_active')
    raw_id_fields = ('member',)


@admin.register(ApprovalAction)
class ApprovalActionAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'approver', 'level', 'action', 'created_at')
    list_filter = ('level', 'action')
    raw_id_fields = ('workflow', 'approver')


@admin.register(EscalationRule)
class EscalationRuleAdmin(admin.ModelAdmin):
    list_display = ('level', 'hours_to_escalate', 'escalate_to', 'is_active')
    list_filter = ('level', 'is_active')
