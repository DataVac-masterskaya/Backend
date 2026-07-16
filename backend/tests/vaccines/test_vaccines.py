from http import HTTPStatus
import pytest

@pytest.mark.django_db 
def test_vaccines_vaccine_pdf_url(api_client, vaccine_pdf_url, vaccine_with_contraindication):
    """Тест получения PDF."""
    vaccine_card = vaccine_with_contraindication['vaccine_card']
    response = api_client.get(vaccine_pdf_url(vaccine_card.id))
    assert response.status_code == HTTPStatus.FOUND

@pytest.mark.django_db
def test_vaccine_pdf_not_found(api_client, vaccine_pdf_url):
    """Тест ошибки 404 при запросе PDF."""
    url = vaccine_pdf_url(99999)
    response = api_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND

#================================================================================================

@pytest.mark.django_db 
def test_vaccines_instruction_url(api_client, vaccine_instruction_url, vaccine_with_contraindication):
    """Тест получения ссылки на инструкцию."""
    vaccine_card = vaccine_with_contraindication['vaccine_card']
    response = api_client.get(vaccine_instruction_url(vaccine_card.id))
    assert response.status_code == HTTPStatus.OK

@pytest.mark.django_db
def test_vaccine_instruction_url_not_found(api_client, vaccine_instruction_url):
    """Тест ошибки 404 при запросе ссылки на инструкцию для несуществующей карточки."""
    url = vaccine_instruction_url(99999)
    response = api_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND

#================================================================================================

@pytest.mark.django_db 
def test_vaccines_instructions_patient_url(api_client, vaccine_instruction_patient_url, vaccine_with_contraindication):
    """Тест получения ссылки на инструкцию для пациентов."""
    vaccine_card = vaccine_with_contraindication['vaccine_card']
    response = api_client.get(vaccine_instruction_patient_url(vaccine_card.id))
    assert response.status_code == HTTPStatus.OK

@pytest.mark.django_db
def test_vaccine_instruction_patient_url_not_found(api_client, vaccine_instruction_patient_url):
    """Тест ошибки 404 при запросе ссылки на инструкцию для специалистов."""
    url = vaccine_instruction_patient_url(99999)
    response = api_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND

#================================================================================================


@pytest.mark.django_db 
def test_vaccines_instructions_specialist_url(api_client, vaccine_instruction_specialist_url, vaccine_with_contraindication):
    """Тест получения ссылки на инструкцию для специалистов."""
    vaccine_card = vaccine_with_contraindication['vaccine_card']
    response = api_client.get(vaccine_instruction_specialist_url(vaccine_card.id))
    assert response.status_code == HTTPStatus.OK

@pytest.mark.django_db
def test_vaccine_instruction_specialist_url_not_found(api_client, vaccine_instruction_specialist_url):
    """Тест ошибки 404 при запросе ссылки на инструкцию для специалистов."""
    url = vaccine_instruction_specialist_url(99999)
    response = api_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND

#================================================================================================