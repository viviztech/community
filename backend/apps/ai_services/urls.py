from django.urls import path
from .views import RecommendationView, AnalyticsView, ChatbotView, BusinessMatchingView

urlpatterns = [
    path('recommendations/', RecommendationView.as_view(), name='recommendations'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),
    path('business-matching/', BusinessMatchingView.as_view(), name='business_matching'),
]
