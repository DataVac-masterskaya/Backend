from django.db import models


class BaseModel(models.Model):
    name = models.CharField(verbose_name='Название', unique=True, null=False)

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


class Category(models.Model):
    name = models.SlugField(verbose_name='Название', unique=True, null=False)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Infection(BaseModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        null=False,
    )

    class Meta:
        verbose_name = 'Инфекция'
        verbose_name_plural = 'Инфекции'

    def __str__(self):
        return self.name
