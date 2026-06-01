from django.db import models


class ContraindicationCategory(models.Model):
    """Хранит категорию противопоказаний к вакцинации."""

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        """Задает таблицу, сортировку и названия модели категории."""

        db_table = 'contraindication_categories'
        ordering = ['name']
        verbose_name = 'Contraindication category'
        verbose_name_plural = 'Contraindication categories'

    def __str__(self) -> str:
        """Возвращает название категории противопоказаний."""
        return self.name


class Contraindication(models.Model):
    """Хранит противопоказание и его поисковые служебные поля."""

    name = models.CharField(max_length=255, unique=True)
    categories = models.ManyToManyField(
        ContraindicationCategory,
        related_name='contraindications',
        db_table='contraindication_categories_contraindications',
        blank=True,
    )
    search_select_count = models.PositiveBigIntegerField(default=0)
    search_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    class Meta:
        """Задает таблицу, сортировку и названия модели противопоказания."""

        db_table = 'contraindications'
        ordering = ['name']
        verbose_name = 'Contraindication'
        verbose_name_plural = 'Contraindications'

    def __str__(self) -> str:
        """Возвращает название противопоказания."""
        return self.name
