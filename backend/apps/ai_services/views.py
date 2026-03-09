"""
AI/ML Service Views for ACTIV Membership Portal.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from apps.members.models import Member
from apps.events.models import Event


class RecommendationView(APIView):
    """AI-powered member recommendation engine."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get member recommendations based on profile similarity."""
        try:
            member = request.user.member_profile
            if not member:
                return Response({
                    'error': 'Member profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get recommendations based on business type, location, and category
            recommendations = self.get_similar_members(member)
            event_recommendations = self.get_event_recommendations(member)
            
            return Response({
                'similar_members': recommendations,
                'recommended_events': event_recommendations,
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_similar_members(self, member, limit=10):
        """Find similar members based on business profile."""
        # Get all active members
        members = Member.objects.filter(
            user__is_active=True
        ).exclude(id=member.id).select_related('user')
        
        if not members:
            return []
        
        # Create feature vectors based on business attributes
        features = []
        member_ids = []
        
        for m in members:
            # Combine business attributes into a feature string
            feature_str = ' '.join(filter(None, [
                m.organization_name or '',
                m.business_type or '',
                m.constitution or '',
                m.business_activities or '',
                str(m.social_category) or '',
                str(m.turnover_range) or '',
            ]))
            features.append(feature_str)
            member_ids.append(m.id)
        
        # Target member feature
        target_feature = ' '.join(filter(None, [
            member.organization_name or '',
            member.business_type or '',
            member.constitution or '',
            member.business_activities or '',
            str(member.social_category) or '',
            str(member.turnover_range) or '',
        ]))
        
        if not target_feature or not features:
            # Return random members if no features available
            return self._get_random_members(members, limit)
        
        # Use TF-IDF for text similarity
        try:
            all_features = features + [target_feature]
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(all_features)
            
            # Calculate similarity
            target_vector = tfidf_matrix[-1]
            feature_vectors = tfidf_matrix[:-1]
            similarities = cosine_similarity(target_vector, feature_vectors)[0]
            
            # Get top similar members
            top_indices = similarities.argsort()[-limit:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:
                    m = members[idx]
                    results.append({
                        'id': str(m.id),
                        'name': m.user.full_name,
                        'email': m.user.email,
                        'organization': m.organization_name,
                        'business_type': m.business_type,
                        'location': f"{m.block.name if m.block else ''} {m.district.name if m.district else ''}".strip(),
                        'similarity_score': float(similarities[idx]),
                    })
            
            return results
        except Exception:
            return self._get_random_members(members, limit)
    
    def _get_random_members(self, members, limit):
        """Get random members as fallback."""
        return [
            {
                'id': str(m.id),
                'name': m.user.full_name,
                'email': m.user.email,
                'organization': m.organization_name,
                'business_type': m.business_type,
                'location': f"{m.block.name if m.block else ''} {m.district.name if m.district else ''}".strip(),
                'similarity_score': 0.0,
            }
            for m in members[:limit]
        ]
    
    def get_event_recommendations(self, member, limit=5):
        """Get event recommendations based on member's interests."""
        upcoming_events = Event.objects.filter(
            event_date__gt= timezone.now(),
            status='published'
        ).order_by('event_date')[:20]
        
        if not upcoming_events:
            return []
        
        # Score events based on relevance
        scored_events = []
        member_interests = ' '.join(filter(None, [
            member.organization_name or '',
            member.business_type or '',
            member.business_activities or '',
        ])).lower()
        
        for event in upcoming_events:
            score = 0.0
            
            # Title relevance
            title_lower = event.title.lower()
            for word in member_interests.split():
                if word in title_lower:
                    score += 0.3
            
            # Description relevance
            desc_lower = event.description.lower()
            for word in member_interests.split():
                if word in desc_lower:
                    score += 0.1
            
            # Location preference
            if member.block and member.block.name in event.venue:
                score += 0.2
            if member.district and member.district.name in event.venue:
                score += 0.2
            
            scored_events.append({
                'id': str(event.id),
                'title': event.title,
                'date': event.event_date,
                'venue': event.venue,
                'price': float(event.ticket_price),
                'relevance_score': min(score, 1.0),
            })
        
        # Sort by relevance score
        scored_events.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_events[:limit]


class AnalyticsView(APIView):
    """AI-powered analytics and insights."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get analytics insights."""
        try:
            # Member growth analytics
            member_growth = self._get_member_growth()
            
            # Category distribution
            category_dist = self._get_category_distribution()
            
            # Geographic distribution
            geo_dist = self._get_geographic_distribution()
            
            # Predictions
            predictions = self._get_predictions()
            
            return Response({
                'member_growth': member_growth,
                'category_distribution': category_dist,
                'geographic_distribution': geo_dist,
                'predictions': predictions,
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_member_growth(self):
        """Get member growth data for last 6 months."""
        growth_data = []
        for i in range(5, -1, -1):
            month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            month_start = month_start - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=32)
            month_end = month_end.replace(day=1)
            
            count = Member.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            
            growth_data.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count,
            })
        return growth_data
    
    def _get_category_distribution(self):
        """Get distribution by social category."""
        from django.db.models import Count
        categories = Member.objects.filter(
            user__is_active=True
        ).values('social_category').annotate(count=Count('id'))
        return [
            {'category': c['social_category'] or 'Unknown', 'count': c['count']}
            for c in categories
        ]
    
    def _get_geographic_distribution(self):
        """Get distribution by district."""
        from django.db.models import Count
        districts = Member.objects.filter(
            user__is_active=True,
            district__isnull=False
        ).values('district__name').annotate(count=Count('id'))
        return [
            {'district': d['district__name'], 'count': d['count']}
            for d in districts
        ]
    
    def _get_predictions(self):
        """Get simple predictions based on trends."""
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        
        # Current month registrations
        current_month = Member.objects.filter(
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).count()
        
        # Last month registrations for comparison
        last_month = Member.objects.filter(
            created_at__month=(timezone.now().replace(day=1) - timedelta(days=1)).month,
            created_at__year=(timezone.now().replace(day=1) - timedelta(days=1)).year
        ).count()
        
        # Simple linear projection
        growth_rate = ((current_month - last_month) / max(last_month, 1)) * 100 if last_month > 0 else 0
        
        return {
            'projected_next_month': int(current_month * (1 + growth_rate / 100)),
            'current_month_registrations': current_month,
            'last_month_registrations': last_month,
            'growth_rate': round(growth_rate, 2),
        }


class ChatbotView(APIView):
    """AI chatbot for member support."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Process chatbot query with rule-based responses."""
        query = request.data.get('query', '').lower().strip()
        
        if not query:
            return Response({
                'error': 'Query is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        response = self._generate_response(query)
        
        return Response({
            'response': response,
            'query': query,
        })
    
    def _generate_response(self, query):
        """Generate response based on keywords."""
        query = query.lower()
        
        # Check for common patterns
        if any(word in query for word in ['membership', 'member', 'join', 'register']):
            return (
                "To become a member of ACTIV:\n"
                "1. Register at our portal with your details\n"
                "2. Complete your profile (80% completion required)\n"
                "3. Apply for membership tier\n"
                "4. Payment processing\n"
                "5. Approval by admin (Block → District → State)\n\n"
                "Visit /register to get started!"
            )
        
        if any(word in query for word in ['event', 'conference', 'workshop']):
            return (
                "ACTIV regularly organizes events including:\n"
                "- Business networking conferences\n"
                "- Industry-specific workshops\n"
                "- Training programs\n"
                "- Annual general meetings\n\n"
                "Check the Events section to see upcoming events and register!"
            )
        
        if any(word in query for word in ['payment', 'fee', 'price', 'cost']):
            return (
                "Membership fees at ACTIV:\n"
                "- Learner: Free\n"
                "- Beginner: ₹500/year\n"
                "- Intermediate: ₹2,000/year\n"
                "- Ideal: ₹10,000/lifetime\n\n"
                "Event tickets are charged separately based on the event."
            )
        
        if any(word in query for word in ['approval', 'status', 'pending']):
            return (
                "Membership approval process:\n"
                "1. Your application is first reviewed at Block level\n"
                "2. Then District level approval\n"
                "3. Finally State level approval\n\n"
                "You can check your application status in your profile."
            )
        
        if any(word in query for word in ['contact', 'support', 'help']):
            return (
                "Contact ACTIV:\n"
                "- Email: support@activ.org.in\n"
                "- Phone: +91-XXX-XXX-XXXX\n"
                "- Office hours: Mon-Sat, 9 AM - 6 PM"
            )
        
        if any(word in query for word in ['document', 'document', 'aadhar', 'pan', 'gst']):
            return (
                "Required documents for membership:\n"
                "- Aadhaar Card (for identity verification)\n"
                "- PAN Card (for business verification)\n"
                "- GST Certificate (if registered)\n"
                "- Udyam Registration (optional, for MSME benefits)"
            )
        
        # Default response
        return (
            "Thank you for your query! I couldn't find specific information about that. "
            "Please try asking about:\n"
            "- Membership registration\n"
            "- Event details\n"
            "- Payment and fees\n"
            "- Approval status\n"
            "- Contact information\n\n"
            "Or email us at support@activ.org.in for further assistance."
        )


class BusinessMatchingView(APIView):
    """AI-powered B2B business matching."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get business matching recommendations."""
        try:
            member = request.user.member_profile
            if not member:
                return Response({
                    'error': 'Member profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            matches = self._find_business_matches(member)
            
            return Response({
                'potential_partners': matches,
                'total_matches': len(matches),
            })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _find_business_matches(self, member, limit=10):
        """Find businesses that could be partners or customers."""
        if not member.organization_name or not member.is_doing_business:
            return []
        
        members = Member.objects.filter(
            user__is_active=True,
            is_doing_business=True
        ).exclude(id=member.id).exclude(
            organization_name=''
        ).select_related('user')[:50]
        
        matches = []
        member_category = member.social_category or ''
        
        for m in members:
            score = 0.0
            
            # Same business type
            if m.business_type == member.business_type:
                score += 0.3
            
            # Same social category
            if m.social_category == member_category:
                score += 0.2
            
            # Geographic proximity (same district)
            if m.district and member.district and m.district.id == member.district.id:
                score += 0.3
            
            # Complementary business activities
            if member.business_activities and m.business_activities:
                if any(word in m.business_activities.lower() for word in member.business_activities.lower().split()[:5]):
                    score += 0.2
            
            if score > 0.2:
                matches.append({
                    'id': str(m.id),
                    'organization': m.organization_name,
                    'owner': m.user.full_name,
                    'business_type': m.business_type,
                    'constitution': m.constitution,
                    'location': f"{m.block.name if m.block else ''} {m.district.name if m.district else ''}".strip(),
                    'match_score': round(score, 2),
                    'contact': m.user.email,
                })
        
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:limit]
