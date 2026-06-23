from django.contrib.auth import get_user_model
from django.db import models

from vaccines.constants import (
    CONTRAINDICATION_TYPE_MAX_LEN,
    DECIMAL_PLACES,
    IS_AVAILABLE_IN_RF_MAX_LEN,
    MAX_AGE_MAX_LEN,
    MAX_DIGITS_SEARCH_WEIGHT,
    MIN_AGE_MAX_LEN,
    NAME_MAX_LEN,
    OFFICIAL_NAME_MAX_LEN,
    PREGNANCY_USAGE_STATUS,
    STATUS_MAX_LEN,
    URL_MAX_LEN,
    VERSION_STATUS_MAX_LEN,
)
from contraindications.models import Contraindication

User = get_user_model()


class PregnancyUsageStatus(models.TextChoices):
    FORBIDDEN = 'forbidden', 'Запрещено'
    CAUTION = 'caution', 'С осторожностью'
    SAFE = 'safe', 'Без опасений'


class VersionStatus(models.TextChoices):
    DRAFT = 'draft', 'Черновик'
    PENDING_MODERATION = 'pending_moderation', 'На модерации'
    APPROVED = 'approved', 'Одобрено'
    REJECTED = 'rejected', 'Отклонено'
    SUPERSEDED = 'superseded', 'Заменена'


class VaccineCardStatus(models.TextChoices):
    ACTIVE = 'active', 'Активна'
    ARCHIVED = 'archived', 'Архивирована'
    DELETED = 'deleted', 'Удалена'


class VaccineCard(models.Model):
    """Карточка вакцины."""

    current_version = models.ForeignKey(
        'VaccineCardVersion',
        null=True,
        on_delete=models.SET_NULL,
        related_name='cards_as_current',
        verbose_name='Текущая версия в работе',
    )
    published_version = models.ForeignKey(
        'VaccineCardVersion',
        null=True,
        on_delete=models.SET_NULL,
        related_name='cards_as_published',
        verbose_name='Опубликованная версия',
    )
    status = models.CharField(
        max_length=STATUS_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Общий статус карточки',
        choices=VaccineCardStatus.choices,
        default=VaccineCardStatus.ACTIVE,
    )
    is_visible = models.BooleanField(default=False, verbose_name='Видимость в поиске')
    search_select_count = models.PositiveBigIntegerField(default=0, verbose_name='Счетчик запросов')
    search_weight = models.DecimalField(
        default=0.00,
        max_digits=MAX_DIGITS_SEARCH_WEIGHT,
        decimal_places=DECIMAL_PLACES,
        verbose_name='Популярность (вес)',
    )
    created_by = models.ForeignKey(
        User, null=True, on_delete=models.PROTECT, related_name='created_vaccine_cards', verbose_name='Автор карточки'
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        on_delete=models.PROTECT,
        related_name='updated_vaccine_cards',
        verbose_name='Редактор карточки',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата редактирования',
    )

    class Meta:
        verbose_name = 'Карточка вакцины'
        verbose_name_plural = 'Карточки вакцин'
        ordering = ('-updated_at',)
        db_table = 'vaccine_cards'

    def __str__(self):
        return f'Карточка {self.id} - {self.status}'


class VaccineCardVersion(models.Model):
    """Версия карточки вакцины."""

    vaccine_card = models.ForeignKey(
        VaccineCard, related_name='versions', on_delete=models.CASCADE, verbose_name='Ссылка на контейнер карточки'
    )
    version_number = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Порядковый номер версии',
    )
    version_status = models.CharField(
        max_length=VERSION_STATUS_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Статус версии',
        choices=VersionStatus.choices,
        default=VersionStatus.DRAFT,
    )
    parent_version = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name='Предыдущая версия',
    )
    moderation_request = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Ссылка на запрос модерации',
    )  # TODO пока как заглушка, потом ссылка на таблицу модерации
    name = models.CharField(
        max_length=NAME_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Название вакцины',
    )
    official_name = models.CharField(
        max_length=OFFICIAL_NAME_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Официальное название',
    )
    is_available_in_rf = models.CharField(
        max_length=IS_AVAILABLE_IN_RF_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Доступность в РФ',
    )
    revision_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата ревизии',
    )
    min_age = models.CharField(max_length=MIN_AGE_MAX_LEN, blank=True, null=True, verbose_name='Минимальный возраст')
    max_age = models.CharField(
        max_length=MAX_AGE_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Максимальный возраст',
    )
    pregnancy_usage_status = models.CharField(
        max_length=PREGNANCY_USAGE_STATUS,
        blank=True,
        null=True,
        verbose_name='Применение при беременности',
        choices=PregnancyUsageStatus.choices,
    )
    storage_conditions = models.TextField(
        blank=True,
        null=True,
        verbose_name='Условия хранения',
    )
    interaction_info = models.TextField(
        blank=True,
        null=True,
        verbose_name='Информация о взаимодействии с препаратами',
    )
    compatibility_info = models.TextField(
        blank=True,
        null=True,
        verbose_name='Информация о совместимости с другими вакцинами',
    )
    comment_ANO = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий АНО',
    )
    ohlp_url = models.URLField(
        max_length=URL_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Ссылка на сайт ОХЛП',
    )
    nonspec_url = models.URLField(
        max_length=URL_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Ссылка на вкладыш',
    )
    pdf_url = models.URLField(
        max_length=URL_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Ссылка на PDF',
    )
    instruction_url = models.URLField(
        max_length=URL_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Ссылка на инструкцию',
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_versions',
        verbose_name='Кем создана версия',
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='approved_versions',
        null=True,
        verbose_name='Кем проверена версия',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Когда создана версия',
    )
    approved_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Кем проверена версия',
    )

    class Meta:
        verbose_name = 'Версия вакцины'
        verbose_name_plural = 'Версии вакцин'
        ordering = ('-created_at',)
        db_table = 'vaccine_card_versions'
        constraints = [models.UniqueConstraint(fields=['vaccine_card', 'version_number'], name='unique_version')]

    def __str__(self):
        return self.name
    

class ContraindicationType(models.TextChoices):
    ABSOLUTE = 'absolute', 'Абсолютное'
    TEMPORARY = 'temporary', 'Временное'


class VaccineCardVersionContraindication(models.Model):
    """Связь версии карточки с противопоказанием."""
    vaccine_card_version = models.ForeignKey(
        VaccineCardVersion,
        on_delete=models.CASCADE,
        related_name='version_contraindications',
        verbose_name='Версия карточки',
    )
    contraindication = models.ForeignKey(
        Contraindication,
        on_delete=models.PROTECT,
        related_name='version_contraindications',
        verbose_name='Противопоказание',
    )
    contraindication_type = models.CharField(
        max_length=CONTRAINDICATION_TYPE_MAX_LEN,
        choices=ContraindicationType.choices,
        default=ContraindicationType.ABSOLUTE,
        verbose_name='Тип противопоказания',
    )

    class Meta:
        db_table = 'vaccine_card_version_contraindications'
        constraints = [models.UniqueConstraint(fields=['vaccine_card_version', 'contraindication'], name='unique_version_contraindication')]
        verbose_name = 'Связь версии с противопоказанием'
        verbose_name_plural = 'Связи версий с противопоказаниями'

    def __str__(self):
        return self.contraindication.name
