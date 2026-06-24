import pytest
from django.contrib.auth import get_user_model

from users.models import Profile

User = get_user_model()

@pytest.mark.django_db
def test_profile_created_when_user_created():
    """Проверяет, что Profile создается при создании пользователя."""
    user = User.objects.create_user(username='test', password='12345')
    assert Profile.objects.filter(user=user).exists()

@pytest.mark.django_db
def test_one_profile_per_user():
    """Проверяет, что создается только один Profile для пользователя."""
    user = User.objects.create_user(username='test', password='12345')
    assert Profile.objects.filter(user=user).count() == 1

@pytest.mark.django_db
def test_profile_user_relation():
    """Проверяет, что Profile создается для конкретного пользователя."""
    user = User.objects.create_user(username='test', password='12345')
    profile = Profile.objects.get(user=user)
    assert profile.user == user
