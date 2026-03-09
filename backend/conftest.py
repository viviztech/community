"""
Pytest configuration and fixtures for ACTIV Membership Portal.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """Return a DRF API client."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Factory fixture to create test users."""
    def _create_user(email='test@example.com', password='testpass123', **kwargs):
        user = User.objects.create_user(
            email=email,
            password=password,
            **kwargs
        )
        return user
    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Return an authenticated API client."""
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def admin_client(api_client, django_user_model):
    """Return an authenticated admin API client."""
    admin = django_user_model.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123'
    )
    api_client.force_authenticate(user=admin)
    return api_client, admin


@pytest.fixture
def member_factory(db):
    """Factory fixture to create test members."""
    from apps.members.models import Member
    
    def _create_member(user=None, **kwargs):
        if user is None:
            user = User.objects.create_user(
                email='member@example.com',
                password='memberpass123'
            )
        member = Member.objects.create(user=user, **kwargs)
        return member
    return _create_member


@pytest.fixture
def sample_member(db, member_factory):
    """Create a sample member for testing."""
    return member_factory(
        organization_name='Test Organization',
        constitution='Proprietorship',
        business_type='Manufacturing'
    )


@pytest.fixture
def sample_members(db, member_factory):
    """Create multiple sample members for testing."""
    members = []
    for i in range(5):
        members.append(member_factory(
            organization_name=f'Organization {i}',
            constitution='Partnership',
            business_type='Services'
        ))
    return members
