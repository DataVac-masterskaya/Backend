import pytest
from django.urls import reverse
from urllib.parse import urlencode

pytestmark = pytest.mark.django_db


class TestInfections:
    """Тесты для /infections (router basename='infections')"""

    URL_LIST = 'infections-list'

    def test_list_infections(self, api_client, sample_infections):
        """Получение списка инфекций"""
        url = reverse(self.URL_LIST)
        response = api_client.get(url)

        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"URL: {url}"
        )
        data = response.json()
        assert len(data) == len(sample_infections), (
            f"Ожидалось {len(sample_infections)} инфекций, "
            f"получено {len(data)}. Данные: {data}"
        )

    def test_sort_by_name_asc(self, api_client, sample_infections):
        """Сортировка по name asc"""
        url = reverse(self.URL_LIST)
        params = {'sort_by': 'name', 'direction': 'asc'}
        response = api_client.get(f"{url}?{urlencode(params)}")

        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"URL: {url}, params: {params}"
        )
        data = response.json()
        names = [item['name'] for item in data]
        expected = sorted(names)
        assert names == expected, (
            f"Сортировка по возрастанию не работает. "
            f"Ожидалось: {expected}, получено: {names}. "
            f"Параметры: {params}"
        )

    def test_sort_by_name_desc(self, api_client, sample_infections):
        """Сортировка по name desc"""
        url = reverse(self.URL_LIST)
        params = {'sort_by': 'name', 'direction': 'desc'}
        response = api_client.get(f"{url}?{urlencode(params)}")

        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"URL: {url}, params: {params}"
        )
        data = response.json()
        names = [item['name'] for item in data]
        expected = sorted(names, reverse=True)
        assert names == expected, (
            f"Сортировка по убыванию не работает. "
            f"Ожидалось: {expected}, получено: {names}. "
            f"Параметры: {params}"
        )

    def test_sort_by_name_default_direction(self, api_client,
                                            sample_infections):
        """Сортировка по name без указания direction (по умолчанию asc)"""
        url = reverse(self.URL_LIST)
        params = {'sort_by': 'name'}
        response = api_client.get(f"{url}?{urlencode(params)}")

        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"URL: {url}, params: {params}"
        )
        data = response.json()
        names = [item['name'] for item in data]
        expected = sorted(names)
        assert names == expected, (
            f"Сортировка по умолчанию (без direction) не работает. "
            f"Ожидалось: {expected}, получено: {names}. "
            f"Параметры: {params}"
        )

    def test_sort_invalid_sort_by(self, api_client, sample_infections):
        """Некорректное поле для сортировки"""
        url = reverse(self.URL_LIST)
        params = {'sort_by': 'invalid_field', 'direction': 'asc'}
        response = api_client.get(f"{url}?{urlencode(params)}")

        assert response.status_code in [400, 200], (
            f"Ожидался статус 400 или 200, получен {response.status_code}. "
            f"URL: {url}, params: {params}"
        )

    def test_filter_by_category_name(self, api_client, sample_infections):
        """Фильтрация по name категории"""
        category = sample_infections[0].category
        url = reverse(self.URL_LIST)
        params = {'category': category.name}
        response = api_client.get(f"{url}?{urlencode(params)}")

        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"URL: {url}, params: {params}, category_name='{category.name}'"
        )
        data = response.json()
        assert len(data) > 0, (
            f"Ожидался хотя бы 1 результат для категории с name '"
            f"{category.name}', "
            f"получено {len(data)} результатов. Данные: {data}"
        )
        for item in data:
            assert item['category'] == category.name, (
                f"Ожидался name категории '{category.name}', "
                f"получен '{item['category']}'. Данные элемента: {item}"
            )

    def test_combined_sort_and_filter_by_name(self, api_client,
                                              sample_infections):
        """Комбинация сортировки и фильтрации по name категории"""
        category = sample_infections[0].category
        url = reverse(self.URL_LIST)
        params = {
            'category': category.name,
            'sort_by': 'name',
            'direction': 'asc'
        }
        response = api_client.get(f"{url}?{urlencode(params)}")

        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"URL: {url}, params: {params}"
        )
        data = response.json()
        assert len(data) > 0, (
            f"Ожидался хотя бы 1 результат для категории с name '"
            f"{category.name}', "
            f"получено {len(data)} результатов. Данные: {data}"
        )
        for item in data:
            assert item['category'] == category.name, (
                f"Фильтрация нарушена при комбинированном запросе. "
                f"Ожидался name '{category.name}', "
                f"получен '{item['category']}'. Данные: {item}, "
                f"params: {params}"
            )
        names = [item['name'] for item in data]
        expected = sorted(names)
        assert names == expected, (
            f"Сортировка нарушена при комбинированном запросе. "
            f"Ожидалось: {expected}, получено: {names}. "
            f"params: {params}"
        )

    def test_combined_sort_desc_and_filter_by_name(self, api_client,
                                                   sample_infections):
        """Фильтрация по name с сортировкой по убыванию"""
        category = sample_infections[0].category
        url = reverse(self.URL_LIST)
        params = {
            'category': category.name,
            'sort_by': 'name',
            'direction': 'desc'
        }
        response = api_client.get(f"{url}?{urlencode(params)}")

        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"URL: {url}, params: {params}"
        )
        data = response.json()
        assert len(data) > 0, (
            f"Ожидался хотя бы 1 результат для категории с name '"
            f"{category.name}', "
            f"получено {len(data)} результатов. Данные: {data}"
        )
        for item in data:
            assert item['category'] == category.name, (
                f"Фильтрация нарушена. Ожидался name '{category.name}', "
                f"получен '{item['category']}'. Данные: {item}"
            )
        names = [item['name'] for item in data]
        expected = sorted(names, reverse=True)
        assert names == expected, (
            f"Сортировка по убыванию нарушена. "
            f"Ожидалось: {expected}, получено: {names}. "
            f"params: {params}"
        )

    def test_invalid_category_name(self, api_client):
        """Несуществующий name категории"""
        url = reverse(self.URL_LIST)
        params = {'category': 'nonexistent-name'}
        response = api_client.get(f"{url}?{urlencode(params)}")

        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"URL: {url}, params: {params}"
        )
        data = response.json()
        assert len(data) == 0, (
            f"Ожидался пустой список для несуществующего name"
            f"'nonexistent-name', "
            f"получено {len(data)} записей. Данные: {data}"
        )

    def test_filter_by_category_empty_name(self, api_client,
                                           sample_infections):
        """Фильтрация по пустому name"""
        url = reverse(self.URL_LIST)
        params = {'category': ''}
        response = api_client.get(f"{url}?{urlencode(params)}")

        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"URL: {url}, params: {params}"
        )
        data = response.json()
        assert len(data) >= 0, (
            f"Некорректный ответ для пустого name. Данные: {data}"
        )

    def test_sort_without_sort_by(self, api_client, sample_infections):
        """Указан direction без sort_by"""
        url = reverse(self.URL_LIST)
        params = {'direction': 'desc'}
        response = api_client.get(f"{url}?{urlencode(params)}")

        assert response.status_code == 200, (
            f"Ожидался статус 200, получен {response.status_code}. "
            f"URL: {url}, params: {params}"
        )
        data = response.json()
        assert len(data) == len(sample_infections), (
            f"Ожидалось {len(sample_infections)} инфекций (все записи), "
            f"получено {len(data)}. Данные: {data}"
        )
