from django.contrib import admin

from vaccines.models import (
    VaccineCard,
    VaccineCardVersion,
    VaccineCardVersionAdministrationMethod,
    VaccineCardVersionContraindication,
    VaccineCardVersionInfection,
    VaccineCardVersionIngredient,
)


class VaccineCardVersionInfectionInline(admin.TabularInline):
    """Инфекции в версии."""

    model = VaccineCardVersionInfection
    extra = 1
    raw_id_fields = ('infection',)
    fields = ('infection',)
    autocomplete_fields = ('infection',)


class VaccineCardVersionIngredientInline(admin.TabularInline):
    """Ингредиенты в версии."""

    model = VaccineCardVersionIngredient
    extra = 1
    raw_id_fields = ('ingredient',)
    fields = ('ingredient', 'role')
    autocomplete_fields = ('ingredient',)


class VaccineCardVersionContraindicationInline(admin.TabularInline):
    """Противопоказания в версии."""

    model = VaccineCardVersionContraindication
    extra = 1
    raw_id_fields = ('contraindication',)
    fields = ('contraindication', 'contraindication_type')
    autocomplete_fields = ('contraindication',)


class VaccineCardVersionAdministrationMethodInline(admin.TabularInline):
    """Способы введения в версии."""

    model = VaccineCardVersionAdministrationMethod
    extra = 1
    raw_id_fields = ('administration_method',)
    fields = ('administration_method', 'age_from', 'age_to', 'note')
    autocomplete_fields = ('administration_method',)


@admin.register(VaccineCardVersion)
class VaccineCardVersionAdmin(admin.ModelAdmin):
    """Админка для версий карточки вакцины."""

    list_display = (
        'id',
        'vaccine_card',
        'version_number',
        'version_status',
        'name',
        'created_at',
    )
    list_filter = ('version_status',)
    search_fields = ('name', 'official_name', 'vaccine_card__id')
    raw_id_fields = ('vaccine_card', 'parent_version', 'created_by', 'approved_by')
    inlines = [
        VaccineCardVersionInfectionInline,
        VaccineCardVersionIngredientInline,
        VaccineCardVersionContraindicationInline,
        VaccineCardVersionAdministrationMethodInline,
    ]

    fieldsets = (
        (
            'Основная информация',
            {
                'fields': (
                    'vaccine_card',
                    'version_number',
                    'version_status',
                    'parent_version',
                    'name',
                    'official_name',
                )
            },
        ),
        (
            'Описание и производитель',
            {
                'fields': (
                    'description',
                    'manufacturer',
                    'is_available_in_rf',
                )
            },
        ),
        (
            'Возраст и беременность',
            {
                'fields': (
                    # 'min_age_months',
                    # 'max_age_months',
                    'age_allowed',
                    'pregnancy_usage_status',
                )
            },
        ),
        (
            'Хранение и взаимодействие',
            {
                'fields': (
                    'storage_conditions',
                    'interaction_info',
                    'compatibility_info',
                    'schedule_info',
                )
            },
        ),
        (
            'Побочные эффекты и показания',
            {
                'fields': (
                    'side_effects',
                    'indications',
                )
            },
        ),
        (
            'Даты',
            {
                'fields': (
                    'registration_date',
                    'revision_date',
                )
            },
        ),
        (
            'Ссылки',
            {
                'fields': (
                    'ohlp_url',
                    'nonspec_url',
                    'instruction_url',
                    'pdf_url',
                    'qr_code_url',
                )
            },
        ),
        (
            'Комментарии',
            {
                'fields': (
                    'comment_source',
                    'comment_ANO',
                )
            },
        ),
        (
            'Аудит',
            {
                'fields': (
                    'created_by',
                    'approved_by',
                ),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change and obj.vaccine_card and not obj.vaccine_card.current_version:
            card = obj.vaccine_card
            card.current_version = obj
            card.published_version = obj
            card.save(update_fields=['current_version', 'published_version', 'updated_at'])

