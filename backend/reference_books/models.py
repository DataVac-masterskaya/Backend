from datavac.constants import (
    LENGTH_TYPE_INGREDIENTS,
    NUMBER_WORDS_NAME,
    NUMBER_WORDS_TYPE,
)
from django.db import models
from django.utils.text import Truncator


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


class MethodsOfAdministration(models.Model):
    """Cпособы введения."""

    name = models.CharField(verbose_name='Название', unique=True)
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True,
        help_text='Описание способа введения',
    )
    list_icon_url = models.ImageField(verbose_name='Иконка в списке', upload_to='admin-methods/list_icons/', null=False)
    detail_image_url = models.ImageField(
        verbose_name='Детальная картинка', upload_to='admin-methods/detail_images/', null=False
    )

    class Meta:
        verbose_name = 'Cпособ введения'
        verbose_name_plural = 'Cпособы введения'

    def __str__(self):
        return self.name[:30]


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
