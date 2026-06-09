from django.db import models
from django.utils.text import Truncator

from datavac.constants import (
    LENGTH_TYPE_INGREDIENTS, NUMBER_WORDS_NAME, NUMBER_WORDS_TYPE
    )
#  from vaccine_cards.models import VaccineCardVersion


class SearchStatsMixin(models.Model):
    """Название и поисковые характеристики."""

    name = models.CharField(verbose_name='Название', unique=True)
    search_select_count = models.PositiveIntegerField(
        verbose_name='Количество поисковых запросов',
        null=False,
        default=0,
    )
    search_weight = models.PositiveIntegerField(
        verbose_name='Поисковой вес',
        null=False,
        default=0,
    )

    class Meta:
        abstract = True


class CategoryInfection(models.Model):
    """Категории инфекций."""

    name = models.SlugField(verbose_name='Название', unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:30]


class Infection(SearchStatsMixin):
    """Инфекции."""

    category = models.ForeignKey(
        CategoryInfection,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        null=False,
    )

    class Meta:
        verbose_name = 'Инфекция'
        verbose_name_plural = 'Инфекции'

    def __str__(self):
        return self.name[:30]


class Ingredients(SearchStatsMixin):
    """Компоненты вакцины."""

    type = models.CharField(
        'Тип ингредиента',
        max_length=LENGTH_TYPE_INGREDIENTS,
        db_index=True,
        help_text='Тип ингредиента (обязательное поле).',
        error_messages={
            'null': 'Тип ингредиента нужно указать!',
        },
    )
    description = models.TextField(
        'Описание',
        blank=True,
        null=True,
        help_text='Описание ингредиента (компонента вакцины)',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        truncated_name = Truncator(self.name).words(NUMBER_WORDS_NAME)
        truncated_type = Truncator(self.type).words(NUMBER_WORDS_TYPE)
        return f'{truncated_name}, ({truncated_type})'


# class VaccineCardVersionIngredients(models.Model):
#     """Ингредиенты в карточках вакцин."""

#     vaccine_card_version = models.ForeignKey(
#         VaccineCardVersion,
#         on_delete=models.CASCADE,
#         related_name='ingredients',
#         verbose_name='Версия вакцины'
#     )
#     ingredient = models.ForeignKey(
#         Ingredients,
#         on_delete=models.PROTECT,
#         related_name='vaccine_versions',
#         verbose_name='Ингредиент'
#     )

#     class Meta:
#         verbose_name = 'Связь версии вакцины с ингредиентом'
#         verbose_name_plural = 'Связи версий вакцин с ингредиентами'
#         unique_together = ('vaccine_card_version', 'ingredient')

#     def __str__(self):
#         return (
#             f'{self.ingredient.name} в версии '
#             f'{self.vaccine_card_version.id}'
#             )
