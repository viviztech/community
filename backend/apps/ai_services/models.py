"""
AI/ML Models for ACTIV Membership Portal.
"""

import uuid
from django.db import models
from django.conf import settings


class MemberCluster(models.Model):
    """Cluster assignments for members based on profile similarity."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.OneToOneField(
        'members.Member', on_delete=models.CASCADE,
        related_name='cluster'
    )
    cluster_id = models.IntegerField()
    cluster_name = models.CharField(max_length=50)
    confidence_score = models.FloatField(default=0.0)
    features = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'member_clusters'
    
    def __str__(self):
        return f"{self.member.user.email} - Cluster {self.cluster_id}"


class MemberRecommendation(models.Model):
    """Member recommendations based on collaborative filtering."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        'members.Member', on_delete=models.CASCADE,
        related_name='recommendations_received'
    )
    recommended_member = models.ForeignKey(
        'members.Member', on_delete=models.CASCADE,
        related_name='recommendations_given'
    )
    score = models.FloatField()
    reason = models.CharField(max_length=255)
    is_viewed = models.BooleanField(default=False)
    is_accepted = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'member_recommendations'
    
    def __str__(self):
        return f"Recommendation: {self.member.user.email} -> {self.recommended_member.user.email}"


class SearchQuery(models.Model):
    """Search query logs for analytics and improvements."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='search_queries'
    )
    query = models.CharField(max_length=255)
    results_count = models.IntegerField(default=0)
    filters_applied = models.JSONField(default=dict)
    search_type = models.CharField(
        max_length=20, choices=[
            ('members', 'Members'),
            ('events', 'Events'),
            ('general', 'General'),
        ], default='general'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_queries'
    
    def __str__(self):
        return f"{self.query} ({self.results_count} results)"


class AnalyticsInsight(models.Model):
    """AI-generated analytics insights."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    insight_type = models.CharField(
        max_length=50, choices=[
            ('membership_trend', 'Membership Trend'),
            ('churn_risk', 'Churn Risk'),
            ('geographic_distribution', 'Geographic Distribution'),
            ('business_matching', 'Business Matching'),
            ('event_popularity', 'Event Popularity'),
        ]
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    data = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'analytics_insights'
    
    def __str__(self):
        return f"{self.title} ({self.get_insight_type_display()})"
