from django.urls import path

from .views import (
    AnalyticsView,
    BusinessMatchingView,
    ChatbotView,
    DocumentVerificationView,
    RecommendationView,
    SemanticSearchView,
)

urlpatterns = [
    path("recommendations/", RecommendationView.as_view(), name="recommendations"),
    path("analytics/", AnalyticsView.as_view(), name="analytics"),
    path("chatbot/", ChatbotView.as_view(), name="chatbot"),
    path("business-matching/", BusinessMatchingView.as_view(), name="business_matching"),
    path("search/", SemanticSearchView.as_view(), name="semantic_search"),
    path("verify-document/", DocumentVerificationView.as_view(), name="document_verification"),
]
