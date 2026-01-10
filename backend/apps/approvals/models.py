"""
Approval Workflow Models for ACTIV Membership Portal.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class ApprovalWorkflow(models.Model):
    """Multi-level approval workflow for member registration."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        IN_PROGRESS = 'in_progress', _('In Progress')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')
    
    class Level(models.TextChoices):
        BLOCK = 'block', _('Block Level')
        DISTRICT = 'district', _('District Level')
        STATE = 'state', _('State Level')
        FINAL = 'final', _('Final Approval')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        'members.Member', on_delete=models.CASCADE,
        related_name='approval_workflows'
    )
    current_level = models.CharField(
        max_length=20, choices=Level.choices,
        default=Level.BLOCK
    )
    status = models.CharField(
        max_length=20, choices=Status.choices,
        default=Status.PENDING
    )
    is_active = models.BooleanField(default=True)
    escalated_at = models.DateTimeField(null=True, blank=True)
    escalation_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'approval_workflows'
        verbose_name = _('Approval Workflow')
        verbose_name_plural = _('Approval Workflows')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Workflow for {self.member.user.full_name} - {self.get_status_display()}"
    
    def get_next_level(self):
        """Get the next approval level."""
        levels = [self.Level.BLOCK, self.Level.DISTRICT, self.Level.STATE, self.Level.FINAL]
        try:
            current_index = levels.index(self.current_level)
            if current_index < len(levels) - 1:
                return levels[current_index + 1]
            return None
        except ValueError:
            return self.Level.BLOCK
    
    def advance_to_next_level(self):
        """Advance to the next approval level."""
        next_level = self.get_next_level()
        if next_level:
            self.current_level = next_level
            self.save()
            return True
        return False


class ApprovalAction(models.Model):
    """Individual approval action at each level."""
    
    class Action(models.TextChoices):
        APPROVE = 'approve', _('Approve')
        REJECT = 'reject', _('Reject')
        REQUEST_INFO = 'request_info', _('Request More Info')
        ESCALATE = 'escalate', _('Escalate')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        ApprovalWorkflow, on_delete=models.CASCADE,
        related_name='actions'
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='approval_actions'
    )
    level = models.CharField(
        max_length=20, choices=ApprovalWorkflow.Level.choices
    )
    action = models.CharField(
        max_length=20, choices=Action.choices
    )
    comments = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'approval_actions'
        verbose_name = _('Approval Action')
        verbose_name_plural = _('Approval Actions')
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.approver.email} - {self.get_action_display()}"


class EscalationRule(models.Model):
    """Escalation rules for each approval level."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    level = models.CharField(
        max_length=20, choices=ApprovalWorkflow.Level.choices,
        unique=True
    )
    hours_to_escalate = models.IntegerField(default=24)
    escalate_to = models.CharField(
        max_length=20, choices=ApprovalWorkflow.Level.choices
    )
    notify_via_email = models.BooleanField(default=True)
    notify_via_sms = models.BooleanField(default=True)
    notify_via_whatsapp = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'escalation_rules'
        verbose_name = _('Escalation Rule')
        verbose_name_plural = _('Escalation Rules')
    
    def __str__(self):
        return f"Escalation for {self.get_level_display()} after {self.hours_to_escalate} hours"
