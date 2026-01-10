from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ApprovalWorkflowViewSet, EscalationRuleViewSet

router = DefaultRouter()
router.register(r'', ApprovalWorkflowViewSet, basename='approval')
router.register(r'escalation-rules', EscalationRuleViewSet, basename='escalation')

urlpatterns = [
    path('', include(router.urls)),
]
