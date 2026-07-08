import pytest

from rest_framework import status

from vaccines.models import VaccineCardStatus


@pytest.mark.django_db
def test_create_vaccine_success(auth_client, minimal_vaccine_payload, admin_vaccines_card_url):
    """Тест успешного создания карточки вакцины."""
    response = auth_client.post(admin_vaccines_card_url, minimal_vaccine_payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['status'] == VaccineCardStatus.DRAFT
    assert 'current_version_id' in response.data


@pytest.mark.django_db
def test_admin_vaccine_detail_success(auth_client, minimal_vaccine_payload, admin_vaccines_card_url, vaccine_detail_url):
    """Тест успешного получения детальной информации о карточке."""
    create_response = auth_client.post(admin_vaccines_card_url, minimal_vaccine_payload, format='json')
    assert create_response.status_code == status.HTTP_201_CREATED
    card_id = create_response.data['id']
    detail_url = vaccine_detail_url(card_id)
    response = auth_client.get(detail_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['id'] == card_id
    assert 'version' in response.data

@pytest.mark.django_db
def test_admin_vaccine_detail_not_found(auth_client, vaccine_detail_url):
    """Тест ошибки 404 при запросе несуществующей карточки."""
    detail_url = vaccine_detail_url(999)
    response = auth_client.get(detail_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_update_vaccine_success(auth_client, minimal_vaccine_payload, admin_vaccines_card_url, minimal_vaccine_payload_update, vaccine_detail_url):
    """Тест обновления карточки вакцины."""
    create_response = auth_client.post(admin_vaccines_card_url, minimal_vaccine_payload, format='json')
    assert create_response.status_code == status.HTTP_201_CREATED
    card_id = create_response.data['id']
    update_url = vaccine_detail_url(card_id)
    response = auth_client.put(update_url, minimal_vaccine_payload_update, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == VaccineCardStatus.DRAFT
    assert 'current_version_id' in response.data
    detail_response = auth_client.get(update_url)
    assert detail_response.data['version']['name'] == 'Измененная вакцина'
