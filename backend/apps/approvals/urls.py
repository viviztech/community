from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ApprovalWorkflowViewSet, EscalationRuleViewSet

workflows_router = DefaultRouter()
workflows_router.register(r"", ApprovalWorkflowViewSet, basename="approval")

escalation_router = DefaultRouter()
escalation_router.register(r"", EscalationRuleViewSet, basename="escalation")

urlpatterns = [
    path("escalation-rules/", include(escalation_router.urls)),
    path("", include(workflows_router.urls)),
]
