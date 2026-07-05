from urllib.parse import urlencode

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestContraindications:
    """Тесты для /contraindications/."""

    URL_LIST = 'contraindication-list'
    URL_CATEGORIES = 'contraindication-category-list'

    def test_list_contraindications(self, api_client, sample_contraindications):
        """Получение списка противопоказаний."""
        url = reverse(self.URL_LIST)
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. URL: {url}'
        data = response.json()
        assert len(data) == len(sample_contraindications), (
            f'Ожидалось {len(sample_contraindications)} противопоказаний, получено {len(data)}. Данные: {data}'
        )
        assert data[0]['name'] == 'Аллергия на компоненты', (
            f"Ожидалось 'Аллергия на компоненты', получено '{data[0]['name']}'. Данные: {data[0]}"
        )

    def test_list_categories(self, api_client, sample_categories):
        """Получение списка категорий противопоказаний."""
        url = reverse(self.URL_CATEGORIES)
        response = api_client.get(url)

        assert response.status_code == 200, f'Ожидался статус 200, получен {response.status_code}. URL: {url}'
        data = response.json()
        assert len(data) >= 2, f'Ожидалось минимум 2 категории, получено {len(data)}. Данные: {data}'

        category_names = [item['name'] for item in data]
        assert 'Абсолютные' in category_names, (
            f"Категория 'Абсолютные' не найдена в ответе. Доступные категории: {category_names}"
        )
        assert 'Относительные' in category_names, (
            f"Категория 'Относительные' не найдена в ответе. Доступные категории: {category_names}"
        )

    def test_categories_filter_no_results(self, api_client):
        """Фильтрация по несуществующей категории."""
        url = reverse(self.URL_LIST)
        params = {'categories': 99999}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        assert len(data) == 0, (
            f'Ожидался пустой список для несуществующей категории 99999, получено {len(data)} записей. Данные: {data}'
        )

    def test_detail_contraindication(self, api_client, sample_contraindications):
        """Получение детальной информации о противопоказании."""
        contraindication = sample_contraindications[0]
        url = reverse('contraindication-detail', kwargs={'pk': contraindication.id})
        response = api_client.get(url)

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, pk={contraindication.id}'
        )
        data = response.json()
        assert data['name'] == contraindication.name, (
            f"Ожидалось имя '{contraindication.name}', получено '{data['name']}'. Данные: {data}"
        )

        category_ids = [c['id'] for c in data['categories']]
        db_category_ids = list(contraindication.categories.values_list('id', flat=True))
        assert any(cat_id in db_category_ids for cat_id in category_ids), (
            f'Категории из ответа {category_ids} '
            f'не найдены в БД {db_category_ids}. '
            f'Противопоказание: {contraindication.name}, данные: {data}'
        )

    def test_contraindication_not_found(self, api_client):
        """Получение несуществующего противопоказания."""
        url = reverse('contraindication-detail', kwargs={'pk': 99999})
        response = api_client.get(url)

        assert response.status_code == 404, (
            f'Ожидался статус 404 для несуществующего противопоказания, получен {response.status_code}. URL: {url}'
        )

    def test_search_contraindications(self, api_client, sample_contraindications):
        """Поиск противопоказаний."""
        url = reverse('contraindication-search')
        params = {'search': 'Аллергия'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        assert len(data) > 0, (
            f"Ожидался хотя бы 1 результат поиска по 'Аллергия', получено {len(data)} результатов. Данные: {data}"
        )
        assert 'Аллергия' in data[0]['name'], (
            f"Ожидалось 'Аллергия' в имени первого результата, получено '{data[0]['name']}'. Данные: {data[0]}"
        )

    def test_search_contraindications_no_results(self, api_client):
        """Поиск противопоказаний без результатов."""
        url = reverse('contraindication-search')
        params = {'search': 'Несуществующее'}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()
        assert len(data) == 0, (
            f"Ожидался пустой список для поиска 'Несуществующее', получено {len(data)} записей. Данные: {data}"
        )

    def test_filter_by_categories_name(self, api_client, sample_contraindications, sample_categories):
        """Фильтрация по названию категории."""
        category = sample_categories[0]
        url = reverse(self.URL_LIST)
        params = {'categories': category.name}
        response = api_client.get(f'{url}?{urlencode(params)}')

        assert response.status_code == 200, (
            f'Ожидался статус 200, получен {response.status_code}. URL: {url}, params: {params}'
        )
        data = response.json()

        if len(data) > 0:
            for item in data:
                category_names = [c['name'] for c in item['categories']]
                assert category.name in category_names, (
                    f"Категория '{category.name}' не найдена в категориях "
                    f"противопоказания '{item['name']}': {category_names}. "
                    f'Параметры запроса: {params}, данные: {item}'
                )
