from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MemberViewSet, GeographicAreaViewSet

router = DefaultRouter()
router.register(r'', MemberViewSet, basename='member')
router.register(r'areas', GeographicAreaViewSet, basename='area')

urlpatterns = [
    path('', include(router.urls)),
]
