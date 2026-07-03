import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_openapi_schema_available_without_auth(api_client):
    """Проверяет, что OpenAPI-схема доступна без авторизации."""
    response = api_client.get(reverse('schema'))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['openapi']


def test_swagger_ui_available_without_auth(api_client):
    """Проверяет, что Swagger UI доступен без авторизации."""
    response = api_client.get(reverse('swagger-ui'))

    assert response.status_code == status.HTTP_200_OK
    assert 'text/html' in response['Content-Type']
