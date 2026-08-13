from django.contrib.auth import get_user_model
from django.db import models

from contraindications.models import Contraindication
from reference_books.models import Infection, Ingredients, MethodsOfAdministration
from vaccines.constants import (
    AGE_ALLOWED_MAX_LEN,
    AGE_GROUP_MAX_LEN,
    COMMENT_MAX_LEN,
    CONTRAINDICATION_TYPE_MAX_LEN,
    DECIMAL_PLACES,
    DEFAULT_VERSION,
    INGREDIENT_ROLE_MAX_LEN,
    MAX_DIGITS_SEARCH_WEIGHT,
    NAME_MAX_LEN,
    OFFICIAL_NAME_MAX_LEN,
    STATUS_MAX_LEN,
    URL_MAX_LEN,
    VERSION_STATUS_MAX_LEN,
)

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
    DRAFT = 'draft', 'Черновик'


class VaccineCard(models.Model):
    """Карточка вакцины."""

    current_version = models.ForeignKey(
        'VaccineCardVersion',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cards_as_current',
        verbose_name='Текущая версия в работе',
    )
    published_version = models.ForeignKey(
        'VaccineCardVersion',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='cards_as_published',
        verbose_name='Опубликованная версия',
    )
    old_id = models.IntegerField(
        verbose_name='Старый ID',
        help_text='ID из старой базы',
        unique=True,
        null=True,
        blank=True,
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
    popularity = models.PositiveIntegerField(blank=True, null=True, verbose_name='Популярность')

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
        default=DEFAULT_VERSION,
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
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name='Предыдущая версия',
        blank=True,
        null=True,
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
    code_name = models.CharField(
        max_length=OFFICIAL_NAME_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Английское название',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание вакцины',
    )
    manufacturer = models.CharField(
        max_length=NAME_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Производитель',
    )
    is_available_in_rf = models.BooleanField(
        blank=True,
        null=True,
        verbose_name='Доступность в РФ',
        default=False,
    )
    old_id = models.IntegerField(
        verbose_name='Старый ID',
        help_text='ID из старой базы',
        unique=True,
        null=True,
        blank=True,
    )
    min_age_days = models.PositiveIntegerField(blank=True, null=True, verbose_name='Минимальный возраст')
    max_age_days = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Максимальный возраст',
    )
    age_allowed = models.CharField(max_length=AGE_ALLOWED_MAX_LEN, default='', verbose_name='Возраст применения')
    pregnancy_usage_status = models.BooleanField(
        blank=True,
        null=True,
        verbose_name='Применение при беременности',
        default=False,
    )
    pregnancy_usage_old = models.TextField(
        blank=True,
        null=True,
        verbose_name='Применение при беременности старое',
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
    schedule_info = models.TextField(
        blank=True,
        null=True,
        verbose_name='Информация о схеме вакцинации',
    )
    side_effects = models.TextField(
        blank=True,
        null=True,
        verbose_name='Побочные эффекты',
    )
    indications = models.TextField(
        blank=True,
        null=True,
        verbose_name='Показания к применению',
    )
    registration_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата регистрации',
    )
    revision_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата ревизии',
    )
    ohlp_url = models.URLField(
        max_length=URL_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Ссылка на сайт ОХЛП',
        help_text='На данный момент не используется, но пусть будет',
    )
    nonspec_url = models.URLField(
        max_length=URL_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Ссылка на вкладыш',
        help_text='Ссылка для специалистов, с .pdf',
    )
    instruction_url = models.URLField(
        max_length=URL_MAX_LEN,
        blank=True,
        null=True,
        help_text='Ссылка на инструкцию для специалистов, берется из ГРЛС',
        verbose_name='Ссылка на инструкцию',
    )
    official_instruction = models.ForeignKey(
        'instructions.OfficialInstruction',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='vaccine_versions',
        help_text='Пока непонятно',
        verbose_name='Официальная инструкция',
    )
    pdf_url = models.URLField(
        max_length=URL_MAX_LEN,
        blank=True,
        null=True,
        help_text='',
        verbose_name='Ссылка на PDF',
        help_text='Ссылка на ПДФ, хранящийся на сайте, создается администраторами',
    )
    qr_code_url = models.URLField(
        max_length=URL_MAX_LEN,
        blank=True,
        null=True,
        help_text='',
        verbose_name='Ссылка на qr',
        help_text='Ссылка на qr, пока непонятно',
    )

    infections = models.ManyToManyField(
        Infection, through='VaccineCardVersionInfection', related_name='vaccine_versions'
    )
    ingredients = models.ManyToManyField(
        Ingredients, through='VaccineCardVersionIngredient', related_name='vaccine_versions'
    )
    contraindications = models.ManyToManyField(
        Contraindication, through='VaccineCardVersionContraindication', related_name='vaccine_versions'
    )
    administration_methods = models.ManyToManyField(
        MethodsOfAdministration, through='VaccineCardVersionAdministrationMethod', related_name='vaccine_versions'
    )
    comment_source = models.CharField(
        max_length=COMMENT_MAX_LEN,
        blank=True,
        null=True,
        verbose_name='Источник комментария АНО',
    )
    comment_ANO = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий АНО',
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
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
        return self.name or f'Версия {self.id}'


# ======================================================================================


class ContraindicationType(models.TextChoices):
    ABSOLUTE = 'absolute', 'Абсолютное'
    TEMPORARY = 'temporary', 'Временное'


class IngredientRoleType(models.TextChoices):
    ACTIVE = 'active', 'Действующее'
    AUXILIARY = 'auxiliary', 'Вспомогательное'


class VaccineCardVersionInfection(models.Model):
    """Связь версии карточки с инфекцией."""

    vaccine_card_version = models.ForeignKey(
        'VaccineCardVersion',
        on_delete=models.CASCADE,
        related_name='infection_relations',
        verbose_name='Версия карточки',
    )

    infection = models.ForeignKey(
        Infection, on_delete=models.PROTECT, related_name='version_infections', verbose_name='Инфекция'
    )

    class Meta:
        db_table = 'vaccine_card_version_infections'
        constraints = [
            models.UniqueConstraint(
                fields=['vaccine_card_version', 'infection'], name='unique_vaccinecard_version_infection'
            )
        ]
        verbose_name = 'Связь версии с инфекцией'
        verbose_name_plural = 'Связи версий с инфекциями'

    def __str__(self):
        return f'{self.vaccine_card_version} - {self.infection.name}'


class VaccineCardVersionIngredient(models.Model):
    """Связь версии карточки с ингредиентом."""

    vaccine_card_version = models.ForeignKey(
        'VaccineCardVersion',
        on_delete=models.CASCADE,
        related_name='ingredient_relations',
        verbose_name='Версия карточки',
    )
    ingredient = models.ForeignKey(
        Ingredients, on_delete=models.PROTECT, related_name='ingredient_relations', verbose_name='Ингредиент'
    )
    role = models.CharField(
        max_length=INGREDIENT_ROLE_MAX_LEN,
        choices=IngredientRoleType.choices,
        default=IngredientRoleType.ACTIVE,
        verbose_name='Роль ингредиента',
    )

    def __str__(self):
        return f'{self.vaccine_card_version} - {self.ingredient.name}'

    class Meta:
        db_table = 'vaccine_card_version_ingredients'
        constraints = [
            models.UniqueConstraint(fields=['vaccine_card_version', 'ingredient'], name='unique_version_ingredient')
        ]
        verbose_name = 'Связь версии с ингредиентом'
        verbose_name_plural = 'Связи версий с ингредиентами'


class VaccineCardVersionContraindication(models.Model):
    """Связь версии карточки с противопоказанием."""

    vaccine_card_version = models.ForeignKey(
        'VaccineCardVersion',
        on_delete=models.CASCADE,
        related_name='contraindications_relations',
        verbose_name='Версия карточки',
    )
    contraindication = models.ForeignKey(
        Contraindication,
        on_delete=models.PROTECT,
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
        constraints = [
            models.UniqueConstraint(
                fields=['vaccine_card_version', 'contraindication'], name='unique_version_contraindication'
            )
        ]
        verbose_name = 'Связь версии с противопоказанием'
        verbose_name_plural = 'Связи версий с противопоказаниями'

    def __str__(self):
        return f'{self.vaccine_card_version} - {self.contraindication.name}'


class VaccineCardVersionAdministrationMethod(models.Model):
    """Связь версии карточки со способами введения."""

    vaccine_card_version = models.ForeignKey(
        'VaccineCardVersion',
        on_delete=models.CASCADE,
        related_name='administration_method_relations',
        verbose_name='Версия карточки',
    )
    administration_method = models.ForeignKey(
        MethodsOfAdministration,
        on_delete=models.PROTECT,
        related_name='version_administration_methods',
        verbose_name='Способ введения',
    )
    age_group = models.CharField(max_length=AGE_GROUP_MAX_LEN, blank=True, null=True, verbose_name='Возрастная группа')
    age_from = models.PositiveIntegerField(null=True, blank=True, verbose_name='Возраст от')
    age_to = models.PositiveIntegerField(null=True, blank=True, verbose_name='Возраст до')
    note = models.TextField(blank=True, null=True, verbose_name='Примечание')

    class Meta:
        db_table = 'vaccine_card_version_administration_methods'
        constraints = [
            models.UniqueConstraint(
                fields=['vaccine_card_version', 'administration_method', 'age_from'],
                name='unique_version_administration_method',
            )
        ]
        verbose_name = 'Связь версии со способом введения'
        verbose_name_plural = 'Связи версий со способами введения'

    def __str__(self):
        return f'{self.vaccine_card_version} - {self.administration_method.name}'
