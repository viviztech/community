from django.contrib import admin

from .models import AnalyticsInsight, MemberCluster, MemberRecommendation, SearchQuery


@admin.register(MemberCluster)
class MemberClusterAdmin(admin.ModelAdmin):
    list_display = ("member", "cluster_id", "cluster_name", "confidence_score")
    raw_id_fields = ("member",)


@admin.register(MemberRecommendation)
class MemberRecommendationAdmin(admin.ModelAdmin):
    list_display = ("member", "recommended_member", "score", "reason")
    raw_id_fields = ("member", "recommended_member")


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("query", "user", "results_count", "search_type")
    raw_id_fields = ("user",)


@admin.register(AnalyticsInsight)
class AnalyticsInsightAdmin(admin.ModelAdmin):
    list_display = ("title", "insight_type", "is_active")
    list_filter = ("insight_type", "is_active")
