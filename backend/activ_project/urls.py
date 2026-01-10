"""
URL configuration for ACTIV Membership Portal.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="ACTIV Membership Portal API",
        default_version='v1',
        description="""
        API Documentation for ACTIV Membership Portal.
        
        ## Features:
        - User Authentication (JWT + Social Login)
        - Member Registration & Profile Management
        - Membership Tiers & Payments
        - Multi-level Approval Workflow
        - Event Management
        - Notifications (Email, SMS, WhatsApp)
        - AI-powered Recommendations
        """,
        terms_of_service="https://activ.org.in/terms/",
        contact=openapi.Contact(email="support@activ.org.in"),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api-docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
    
    # Authentication
    path('api/v1/auth/', include('apps.accounts.urls')),
    
    # Core
    path('api/v1/', include('apps.core.urls')),
    
    # Members
    path('api/v1/members/', include('apps.members.urls')),
    
    # Memberships
    path('api/v1/memberships/', include('apps.memberships.urls')),
    
    # Approvals
    path('api/v1/approvals/', include('apps.approvals.urls')),
    
    # Events
    path('api/v1/events/', include('apps.events.urls')),
    
    # Payments
    path('api/v1/payments/', include('apps.payments.urls')),
    
    # Notifications
    path('api/v1/notifications/', include('apps.notifications.urls')),
    
    # AI Services
    path('api/v1/ai/', include('apps.ai_services.urls')),
]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom Admin Site Header
admin.site.site_header = "ACTIV Membership Portal - Admin"
admin.site.site_title = "ACTIV Portal"
admin.site.index_title = "Dashboard"
