from django.urls import path

from .views import (AnalyticsView, BusinessMatchingView, ChatbotView,
                    RecommendationView)

urlpatterns = [
    path("recommendations/", RecommendationView.as_view(), name="recommendations"),
    path("analytics/", AnalyticsView.as_view(), name="analytics"),
    path("chatbot/", ChatbotView.as_view(), name="chatbot"),
    path(
        "business-matching/", BusinessMatchingView.as_view(), name="business_matching"
    ),
]
