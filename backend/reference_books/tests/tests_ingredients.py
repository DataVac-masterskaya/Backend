from django.test import TestCase
from django.core.exceptions import ValidationError
from reference_books.models import Ingredients


class IngredientsModelTest(TestCase):

    def setUp(self):
        # Базовый объект для тестов
        self.ingredient = Ingredients.objects.create(
            name='Гидроксид алюминия',
            type='adjuvant',
            description='Описание ингредиента'
        )

    def test_valid_ingredient_creation(self):
        """Проверка корректного создания объекта"""
        self.assertEqual(self.ingredient.name, 'Гидроксид алюминия')
        self.assertEqual(self.ingredient.type, 'adjuvant')
        self.assertEqual(self.ingredient.description, 'Описание ингредиента')

    def test_required_fields(self):
        """Проверка обязательных полей"""
        with self.assertRaises(ValidationError):
            Ingredients.objects.create(type='adjuvant')  # отсутствует name

        with self.assertRaises(ValidationError):
            Ingredients.objects.create(name='Тестовое')  # отсутствует type

    def test_name_max_length(self):
        """Проверка максимальной длины поля name"""
        max_length = Ingredients._meta.get_field('name').max_length
        long_name = 'a' * (max_length + 1)

        with self.assertRaises(ValidationError):
            Ingredients.objects.create(
                name=long_name,
                type='adjuvant'
            )

    def test_type_validation(self):
        """Проверка валидности типа"""
        valid_types = ['adjuvant', 'stabilizer', 'active']

        for type in valid_types:
            ingredient = Ingredients.objects.create(
                name='Тестовое',
                type=type,
                description='Тест'
            )
            self.assertEqual(ingredient.type, type)

    def test_unique_name(self):
        """Проверка уникальности названия"""
        with self.assertRaises(ValidationError):
            Ingredients.objects.create(
                name=self.ingredient.name,
                type='adjuvant'
            )

    def test_str_method(self):
        """Проверка метода __str__"""
        self.assertEqual(str(self.ingredient), self.ingredient.name)

    def test_description_optional(self):
        """Проверка необязательности поля description"""
        ingredient = Ingredients.objects.create(
            name='Тестовое',
            type='adjuvant'
        )
        self.assertIsNone(ingredient.description)
