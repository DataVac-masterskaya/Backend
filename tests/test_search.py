from urllib.parse import urlencode

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestSearchSuggestions:
    """Тесты для /search/suggestions/."""

    URL = 'search-suggestions'

    def test_empty_query(self, api_client):
        """Пустой поисковый запрос — возвращает пустые группы."""
        url = reverse(self.URL)
        params = {'q': ''}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}.'
        data = response.json()

        for group in ['vaccines', 'infections', 'ingredients', 'contraindications', 'instructions']:
            assert group in data, f'Ожидалась группа "{group}" в ответе. Ключи: {list(data.keys())}'
            assert isinstance(data[group], list), f'Группа "{group}" должна быть списком, получен {type(data[group])}'
            assert len(data[group]) == 0, (
                f'Группа "{group}" должна быть пустой для пустого запроса, получено {len(data[group])} элементов.'
            )

    def test_no_query_param(self, api_client):
        """Запрос без параметра q."""
        url = reverse(self.URL)
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}.'
        data = response.json()

        for group in ['vaccines', 'infections', 'ingredients', 'contraindications', 'instructions']:
            assert group in data
            assert isinstance(data[group], list)

    def test_search_vaccines(self, api_client, sample_vaccine_versions):
        """Поиск вакцин по названию."""
        url = reverse(self.URL)
        params = {'q': 'Инфанрикс'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. params: {params}'
        data = response.json()

        assert 'vaccines' in data, f'Ожидалась группа "vaccines" в ответе. Ключи: {list(data.keys())}'
        assert len(data['vaccines']) > 0, f'Ожидался хотя бы 1 результат в группе vaccines. Данные: {data}'

        item = data['vaccines'][0]
        assert 'id' in item, f'Ожидалось поле "id" в элементе поиска. Ключи: {list(item.keys())}'
        assert isinstance(item['id'], int), f'id должен быть int, получен {type(item["id"])}: {item["id"]}'
        assert 'name' in item, f'Ожидалось поле "name" в элементе поиска. Ключи: {list(item.keys())}'
        assert isinstance(item['name'], str) and len(item['name']) > 0
        assert 'Инфанрикс' in item['name'], f'Ожидалось "Инфанрикс" в названии, получено "{item["name"]}"'
        assert 'score' in item, f'Ожидалось поле "score" в элементе поиска. Ключи: {list(item.keys())}'
        assert isinstance(item['score'], (str, float)), (
            f'score должен быть строкой или числом, получен {type(item["score"])}'
        )

    def test_search_infections(self, api_client, sample_infections):
        """Поиск инфекций по названию."""
        url = reverse(self.URL)
        params = {'q': 'Дифтерия'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200
        data = response.json()

        assert 'infections' in data
        assert len(data['infections']) > 0, f'Ожидался хотя бы 1 результат в группе infections. Данные: {data}'

        item = data['infections'][0]
        assert 'id' in item
        assert isinstance(item['id'], int)
        assert 'name' in item
        assert 'Дифтерия' in item['name']
        assert 'score' in item

    def test_search_ingredients(self, api_client, sample_ingredients):
        """Поиск ингредиентов по названию."""
        url = reverse(self.URL)
        params = {'q': 'Алюминия'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200
        data = response.json()

        assert 'ingredients' in data
        assert len(data['ingredients']) > 0, f'Ожидался хотя бы 1 результат в группе ingredients. Данные: {data}'

        item = data['ingredients'][0]
        assert 'id' in item
        assert isinstance(item['id'], int)
        assert 'name' in item
        assert 'Алюминия' in item['name']
        assert 'score' in item

    def test_search_contraindications(self, api_client, sample_contraindications):
        """Поиск противопоказаний по названию."""
        url = reverse(self.URL)
        params = {'q': 'Бронхиальная'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200
        data = response.json()

        assert 'contraindications' in data
        assert len(data['contraindications']) > 0, (
            f'Ожидался хотя бы 1 результат в группе contraindications. Данные: {data}'
        )

        item = data['contraindications'][0]
        assert 'id' in item
        assert isinstance(item['id'], int)
        assert 'name' in item
        assert 'Бронхиальная' in item['name']
        assert 'score' in item

    def test_search_instructions(self, api_client, sample_official_instructions):
        """Поиск инструкций по названию."""
        url = reverse(self.URL)
        params = {'q': 'АКДС'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200
        data = response.json()

        assert 'instructions' in data
        if len(data['instructions']) > 0:
            item = data['instructions'][0]
            assert 'id' in item
            assert isinstance(item['id'], int)
            assert 'name' in item or 'title' in item
            assert 'score' in item

    def test_search_no_results(self, api_client):
        """Поиск без результатов — все группы пустые."""
        url = reverse(self.URL)
        params = {'q': 'НесуществующийЗапросXYZ'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200
        data = response.json()

        for group in ['vaccines', 'infections', 'ingredients', 'contraindications', 'instructions']:
            assert group in data
            assert len(data[group]) == 0, f'Группа "{group}" должна быть пустой, получено {len(data[group])} элементов.'

    def test_response_structure(self, api_client):
        """Проверка общей структуры ответа."""
        url = reverse(self.URL)
        params = {'q': 'test'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200
        data = response.json()

        expected_groups = ['vaccines', 'infections', 'ingredients', 'contraindications', 'instructions']
        for group in expected_groups:
            assert group in data, f'Ожидалась группа "{group}" в ответе. Ключи: {list(data.keys())}'
            assert isinstance(data[group], list), f'Группа "{group}" должна быть списком'

    def test_element_structure(self, api_client, sample_vaccine_versions):
        """Проверка структуры элемента поиска."""
        url = reverse(self.URL)
        params = {'q': 'Инфанрикс'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200
        data = response.json()

        if len(data['vaccines']) > 0:
            item = data['vaccines'][0]

            required_fields = ['id', 'name', 'score']
            for field in required_fields:
                assert field in item, f'Ожидалось поле "{field}" в элементе. Ключи: {list(item.keys())}'

            assert isinstance(item['id'], int), f'id должен быть int, получен {type(item["id"])}'
            assert isinstance(item['name'], str) and len(item['name']) > 0, 'name должен быть непустой строкой'
            assert isinstance(item['score'], (str, float, int)), (
                f'score должен быть строкой или числом, получен {type(item["score"])}'
            )
