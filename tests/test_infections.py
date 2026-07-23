from urllib.parse import urlencode

import pytest
from django.urls import reverse
from utils import get_count, get_results

pytestmark = pytest.mark.django_db


class TestInfections:
    """Тесты для /infections."""

    URL_LIST = 'infections-list'

    def test_list_infections(self, api_client, sample_infections):
        """Получение списка инфекций с проверкой структуры."""
        url = reverse(self.URL_LIST)
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. URL: {url}'
        data = response.json()
        results = get_results(data)
        count = get_count(data, results)
        assert count == len(sample_infections), (
            f'Ожидалось {len(sample_infections)} инфекций, получено {count}. Данные: {data}'
        )
        assert len(results) > 0, f'Список инфекций пуст, но в фикстуре создано {len(sample_infections)} записей.'

        item = results[0]

        assert 'id' in item, f'Ожидалось поле "id" в элементе. Ключи: {list(item.keys())}'
        assert isinstance(item['id'], int), (
            f'Поле "id" должно быть целым числом, получен тип {type(item["id"])}. Значение: {item["id"]}'
        )
        assert 'name' in item, f'Ожидалось поле "name" в элементе. Ключи: {list(item.keys())}'
        assert isinstance(item['name'], str) and len(item['name']) > 0, (
            f'Поле "name" должно быть непустой строкой, получен тип {type(item["name"])}. Значение: {item["name"]}'
        )
        assert 'category' in item, f'Ожидалось поле "category" в элементе. Ключи: {list(item.keys())}'
        assert item['category'] in ['national_calendar', 'extended', 'other'], (
            f"Недопустимая категория: '{item['category']}'. "
            f'Допустимые: [national_calendar, extended, other]. '
            f'Данные элемента: {item}'
        )
        assert 'popularity' in item, f'Ожидалось поле "popularity" в элементе. Ключи: {list(item.keys())}'
        assert isinstance(item['popularity'], int), (
            f'Поле "popularity" должно быть целым числом, получен тип {type(item["popularity"])}. '
            f'Значение: {item["popularity"]}'
        )

    @pytest.mark.parametrize(
        'category_value',
        [
            'national_calendar',
            'extended',
            'other',
        ],
    )
    def test_filter_by_category(self, api_client, sample_infections, category_value):
        """Фильтрация по категории."""
        url = reverse(self.URL_LIST)
        params = {'category': category_value}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        assert len(results) > 0, (
            f'Фильтр по category={category_value} не вернул результатов. Ожидался хотя бы 1 элемент. Данные: {data}'
        )
        for item in results:
            assert item['category'] == category_value, (
                f"Ожидалась категория '{category_value}' для инфекции "
                f"'{item.get('name')}', получена '{item['category']}'. "
                f'Данные элемента: {item}'
            )

    def test_filter_by_category_invalid(self, api_client):
        """Фильтрация по несуществующей категории — пустой список."""
        url = reverse(self.URL_LIST)
        params = {'category': 'invalid_category'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        assert len(results) == 0, (
            f"Ожидался пустой список для category='{params['category']}', "
            f'получено {len(results)} записей. Данные: {results}'
        )

    def test_sort_by_name_asc(self, api_client, sample_infections):
        """Сортировка по name_asc (по умолчанию)."""
        url = reverse(self.URL_LIST)
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. URL: {url}'
        data = response.json()
        results = get_results(data)
        names = [item['name'] for item in results]
        assert names == sorted(names), (
            f'Сортировка по названию (asc) нарушена. Ожидалось: {sorted(names)}, получено: {names}'
        )

    def test_sort_by_name_desc(self, api_client, sample_infections):
        """Сортировка по name_desc."""
        url = reverse(self.URL_LIST)
        params = {'sort': 'name_desc'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        names = [item['name'] for item in results]
        assert names == sorted(names, reverse=True), (
            f'Сортировка по названию (desc) нарушена. Ожидалось: {sorted(names, reverse=True)}, получено: {names}'
        )

    def test_pagination(self, api_client, sample_infections):
        """Пагинация через limit."""
        url = reverse(self.URL_LIST)
        params = {'limit': 2}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        results = get_results(data)
        count = get_count(data, results)
        assert len(results) == 2, (
            f'Ожидалось 2 элемента на странице (limit=2), получено {len(results)}. Данные: {results}'
        )
        assert count == len(sample_infections), (
            f'Общее количество записей не совпадает с фикстурой. Ожидалось {len(sample_infections)}, получено {count}.'
        )
