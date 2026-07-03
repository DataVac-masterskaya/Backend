import pytest
from typing import cast
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from rest_framework.test import APIClient

User = cast(type[AbstractUser], get_user_model())


@pytest.fixture
def normal_user(db) -> AbstractUser:
    return User.objects.create_user(username='test_user_normal', password='password')


@pytest.fixture
def admin_user(db) -> AbstractUser:
    return User.objects.create_superuser(username='test_admin', password='password')


@pytest.fixture
def anonymous_client() -> APIClient:
    return APIClient()


@pytest.fixture
def normal_client(normal_user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=normal_user)
    return client


@pytest.fixture
def admin_client(admin_user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client
