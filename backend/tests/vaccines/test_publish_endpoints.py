from http import HTTPStatus
import pytest

@pytest.mark.django_db 
def test_vaccines_list(api_client, vaccine_list_url):
    """Тест списка вакцин."""
    response = api_client.get(vaccine_list_url)
    assert response.status_code == HTTPStatus.OK
    data = response.data
    assert 'count' in data
    assert 'results' in data
    results = data['results']
    assert isinstance(results, list)
    if results:
        item = results[0]
        assert 'id' in item
        assert 'name' in item
        assert 'official_name' in item

@pytest.mark.django_db
def test_detail_vaccines(api_client, vaccine_publish_detail_url, vaccine_with_contraindication):
    """Тест детального просмотра карточки вакцины."""
    vaccine_card = vaccine_with_contraindication['vaccine_card']
    response = api_client.get(vaccine_publish_detail_url(vaccine_card.id))
    assert response.status_code == HTTPStatus.OK
    assert response.data['id'] == vaccine_card.id
    assert 'name' in response.data
    assert 'official_name' in response.data
