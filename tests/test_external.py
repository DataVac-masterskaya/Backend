import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestExternalRedirects:
    """Тесты для /vaccines/."""

    def test_support_redirect(self, api_client):
        """Редирект /external/support."""
        url = reverse('external-support')
        response = api_client.get(url)

        assert response.status_code == 302, (
            f'Ожидался статус 302 (редирект), получен {response.status_code}. URL: {url}'
        )
        assert response.url == 'https://vaccina.info/donate', (
            f'Ожидался редирект на https://vaccina.info/donate, получен {response.url}'
        )

    def test_about_redirect(self, api_client):
        """Редирект /external/about."""
        url = reverse('external-about')
        response = api_client.get(url)

        assert response.status_code == 302, (
            f'Ожидался статус 302 (редирект), получен {response.status_code}. URL: {url}'
        )
        assert response.url == 'https://vaccina.info/team#submenu:menu-about', (
            f'Ожидался редирект на https://vaccina.info/team#submenu:menu-about, получен {response.url}'
        )

    def test_feedback_redirect(self, api_client):
        """Редирект /external/feedback."""
        url = reverse('external-feedback')
        response = api_client.get(url)

        assert response.status_code == 302, (
            f'Ожидался статус 302 (редирект), получен {response.status_code}. URL: {url}'
        )
        assert response.url == 'https://vaccina.info/questions', (
            f'Ожидался редирект на https://vaccina.info/questions, получен {response.url}'
        )

    def test_privacy_redirect(self, api_client):
        """Редирект /external/privacy."""
        url = reverse('external-privacy')
        response = api_client.get(url)

        assert response.status_code == 302, (
            f'Ожидался статус 302 (редирект), получен {response.status_code}. URL: {url}'
        )
        assert response.url == 'https://shop.vaccina.info/privacy', (
            f'Ожидался редирект на https://shop.vaccina.info/privacy, получен {response.url}'
        )
