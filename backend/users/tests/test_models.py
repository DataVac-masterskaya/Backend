import pytest
from django.contrib.auth import get_user_model

from users.models import Profile

User = get_user_model()


@pytest.fixture
def test_user():
    """Фикстура для создания тестового пользователя."""
    return User.objects.create_user(username='test', password='12345')


@pytest.mark.django_db
def test_profile_created_when_user_created(test_user):
    """Проверяет, что Profile создается при создании пользователя."""
    assert Profile.objects.filter(user=test_user).exists()

@pytest.mark.django_db
def test_one_profile_per_user(test_user):
    """Проверяет, что создается только один Profile для пользователя."""
    assert Profile.objects.filter(user=test_user).count() == 1


@pytest.mark.django_db
def test_profile_user_relation(test_user):
    """Проверяет, что Profile создается для конкретного пользователя."""
    profile = Profile.objects.get(user=test_user)
    assert profile.user == test_user
