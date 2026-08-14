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
    parsed_text = models.TextField(
        blank=True,
        default='',
        verbose_name='Текст инструкции (из парсинга)',
    )
    content_hash = models.CharField(
        max_length=64,
        blank=True,
        default='',
        verbose_name='Хэш текста инструкции',
    )
    last_checked_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Дата последней проверки источника',
    )
    has_update = models.BooleanField(
        default=False,
        verbose_name='Обнаружено обновление',
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
