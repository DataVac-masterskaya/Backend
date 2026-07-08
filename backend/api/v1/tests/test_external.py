import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Создает API-клиент для pytest-тестов."""
    return APIClient()


def test_feedback_redirects_to_external_url(api_client):
    """Проверяет редирект на страницу обратной связи."""
    response = api_client.get('/api/v1/external/feedback')

    assert response.status_code == status.HTTP_302_FOUND
    assert response['Location'] == 'https://vaccina.info/questions'
