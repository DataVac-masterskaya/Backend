from django.db import models


class ContraindicationCategory(models.Model):
    """Хранит категорию противопоказаний к вакцинации."""

    name = models.CharField(max_length=255, unique=True, verbose_name='Название категории')

    class Meta:
        """Задает таблицу, сортировку и названия модели категории."""

        db_table = 'contraindication_categories'
        ordering = ['name']
        verbose_name = 'Категория противопоказания'
        verbose_name_plural = 'Категории противопоказаний'

    def __str__(self) -> str:
        """Возвращает название категории противопоказаний."""
        return self.name


class Contraindication(models.Model):
    """Хранит противопоказание и его поисковые служебные поля."""

    name = models.CharField(max_length=255, unique=True, verbose_name='Название противопоказания')
    old_id = models.IntegerField(
        verbose_name='Старый ID',
        help_text='ID из старой базы',
        unique=True,
        null=True,
        blank=True,
    )
    categories = models.ManyToManyField(
        ContraindicationCategory,
        related_name='contraindications',
        db_table='contraindication_categories_contraindications',
        blank=True,
        verbose_name='Категории',
    )
    subcategory = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Подкатегория',
    )
    search_select_count = models.PositiveBigIntegerField(default=0, verbose_name='Количество поисковых запросов')
    search_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Поисковой вес')
    popularity = models.PositiveIntegerField(blank=True, null=True, verbose_name='Популярность')

    class Meta:
        """Задает таблицу, сортировку и названия модели противопоказания."""

        db_table = 'contraindications'
        ordering = ['name']
        verbose_name = 'Противопоказание'
        verbose_name_plural = 'Противопоказания'

    def __str__(self) -> str:
        """Возвращает название противопоказания."""
        return self.name
