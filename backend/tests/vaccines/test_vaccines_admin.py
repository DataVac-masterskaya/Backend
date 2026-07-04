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
