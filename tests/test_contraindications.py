from urllib.parse import urlencode

import pytest
from django.urls import reverse
from utils import get_results

pytestmark = pytest.mark.django_db


class TestContraindications:
    """Тесты для /contraindications/."""

    URL_LIST = 'contraindication-list'

    def test_list_contraindications(self, api_client, sample_contraindications):
        """Получение списка противопоказаний с проверкой структуры."""
        url = reverse(self.URL_LIST)
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()
        results = get_results(data)
        assert len(results) == len(sample_contraindications)
        assert len(results) > 0, 'Список противопоказаний пуст'

        item = results[0]

        assert 'id' in item, f'Ожидалось поле "id". Ключи: {list(item.keys())}'
        assert isinstance(item['id'], int)
        assert 'name' in item
        assert isinstance(item['name'], str) and len(item['name']) > 0
        assert 'popularity' in item, f'Ожидалось поле "popularity". Ключи: {list(item.keys())}'
        assert isinstance(item['popularity'], int)

        assert 'category' in item, f'Ожидалось поле "category". Ключи: {list(item.keys())}'

        if 'subcategory' in item:
            assert item['subcategory'] is None or isinstance(item['subcategory'], str)

    def test_filter_by_category_name(self, api_client, sample_contraindications, sample_contraindication_categories):
        """Фильтрация по названию категории."""
        category = sample_contraindication_categories[0]
        url = reverse(self.URL_LIST)
        params = {'category': category.name}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200
        data = response.json()
        results = get_results(data)
        assert len(results) > 0, (
            f'Ожидался хотя бы 1 результат для category={category.name}, получено {len(results)}. Данные: {results}'
        )
        for item in results:
            category_data = item.get('category')
            if isinstance(category_data, dict):
                assert category_data['name'] == category.name, (
                    f"Ожидалась категория '{category.name}', получена '{category_data['name']}'. Данные: {item}"
                )

    def test_filter_by_invalid_category(self, api_client):
        """Фильтрация по несуществующей категории."""
        url = reverse(self.URL_LIST)
        params = {'category': 'НесуществующаяКатегория'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200
        data = response.json()
        results = get_results(data)
        assert len(results) == 0, f'Ожидался пустой список, получено {len(results)} записей.'

    def test_sort_by_name(self, api_client, sample_contraindications):
        """Сортировка по названию."""
        url = reverse(self.URL_LIST)
        params = {'sort': 'name'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200
        data = response.json()
        results = get_results(data)
        if len(results) > 1:
            names = [item['name'] for item in results]
            assert names == sorted(names), f'Сортировка по name: ожидался алфавитный порядок. Получено: {names}'

    def test_sort_by_popularity(self, api_client, sample_contraindications):
        """Сортировка по популярности (search_select_count)."""
        url = reverse(self.URL_LIST)
        params = {'sort': 'popularity'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200
        data = response.json()
        results = get_results(data)
        if len(results) > 1:
            popularity_values = [item['popularity'] for item in results]
            assert popularity_values == sorted(popularity_values, reverse=True), (
                f'Сортировка по popularity. Получено: {popularity_values}'
            )
