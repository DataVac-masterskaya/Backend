from django.db import models


class OfficialInstruction(models.Model):
    """Хранит официальную инструкцию к вакцине."""

    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Заголовок',
    )
    url = models.URLField(max_length=500, unique=True)
    source = models.CharField(
        max_length=255,
        default='ГРЛС',
        verbose_name='Источник',
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание',
    )
    search_select_count = models.PositiveBigIntegerField(
        default=0,
        verbose_name='Количество поисковых запросов',
    )
    search_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Поисковой вес',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Задает таблицу, сортировку и названия модели инструкции."""

        db_table = 'official_instructions'
        ordering = ['title']
        verbose_name = 'Официальная инструкция'
        verbose_name_plural = 'Официальные инструкции'

    def __str__(self) -> str:
        """Возвращает название официальной инструкции."""
        return self.title
