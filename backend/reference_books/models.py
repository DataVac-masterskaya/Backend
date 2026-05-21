from django.db import models


class BaseModel(models.Model):
    name = models.CharField(
        verbose_name='Название',
        null=True,
    )

    search_select_count = models.PositiveIntegerField(
        verbose_name='Количество поисковых запросов',
        null=False,
    )

    search_weight = models.PositiveIntegerField(
        verbose_name='Поисковой вес',
        null=False,
    )

    class Meta:
        abstract = True


class Category(models.Model):
    name = models.CharField(
        verbose_name='Название',
        null=True,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Infection(BaseModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        null=False,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Инфекция'
        verbose_name_plural = 'Инфекции'

    def __str__(self):
        return self.name
