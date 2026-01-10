from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SocialLoginView

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('social/', SocialLoginView.as_view(), name='social-login'),
    path('', include(router.urls)),
]
