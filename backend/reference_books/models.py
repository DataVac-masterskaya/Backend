from django.db import models


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
