import pytest
from rest_framework import status
from django.urls import reverse

from vaccines.models import VaccineCardStatus


@pytest.mark.django_db
def test_create_vaccine_success(auth_client, minimal_vaccine_payload, admin_vaccines_card_url):
    """Тест успешного создания карточки вакцины."""
    response = auth_client.post(admin_vaccines_card_url, minimal_vaccine_payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['status'] == VaccineCardStatus.DRAFT
    assert 'current_version_id' in response.data


@pytest.mark.django_db
def test_admin_vaccine_detail_success(api_client, test_user, minimal_vaccine_payload, admin_vaccines_card_url):
    """Тест успешного получения детальной информации о карточке."""
    api_client.force_authenticate(user=test_user)
    create_response = api_client.post(admin_vaccines_card_url, minimal_vaccine_payload, format='json')
    assert create_response.status_code == status.HTTP_201_CREATED
    card_id = create_response.data['id']
    detail_url = reverse('admin-vaccine-detail', kwargs={'id': card_id})
    response = api_client.get(detail_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == card_id
    assert 'version' in response.data

@pytest.mark.django_db
def test_admin_vaccine_detail_not_found(api_client, test_user):
    """Тест ошибки 404 при запросе несуществующей карточки."""
    api_client.force_authenticate(user=test_user)
    detail_url = reverse('admin-vaccine-detail', kwargs={'id': 99999})
    response = api_client.get(detail_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND