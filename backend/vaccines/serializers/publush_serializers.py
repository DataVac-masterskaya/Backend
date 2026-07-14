from collections import defaultdict

from rest_framework import serializers

from vaccines.models import (
    ContraindicationType,
    IngredientRoleType,
    VaccineCard,
)
from vaccines.utils import format_age


class VaccineCardShort(serializers.ModelSerializer):
    """Сериализатор для краткой информации о карточке вакцины."""

    name = serializers.CharField(source='current_version.name')
    official_name = serializers.CharField(source='current_version.official_name')
    infections = serializers.SerializerMethodField()

    class Meta:
        model = VaccineCard
        fields = ('id', 'name', 'official_name', 'infections')

    def get_infections(self, obj):
        if obj.current_version:
            return list(obj.current_version.infections.values_list('name', flat=True))
        return []


class VaccineCardDetail(VaccineCardShort):
    """Сериализатор для детального просмотра карточки вакцины."""

    revision_date = serializers.CharField(source='current_version.revision_date', allow_null=True)
    pregnancy_status = serializers.CharField(source='current_version.pregnancy_usage_status', allow_null=True)
    storage_conditions = serializers.CharField(source='current_version.storage_conditions', allow_null=True)
    contraindications = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    age_allowed = serializers.SerializerMethodField()
    administration_methods = serializers.SerializerMethodField()
    instruction_patient_url = serializers.URLField(source='current_version.nonspec_url', allow_null=True)
    instruction_specialist_url = serializers.URLField(source='current_version.ohlp_url', allow_null=True)
    qr_code_url = serializers.URLField(source='current_version.qr_code_url', allow_null=True)

    class Meta(VaccineCardShort.Meta):
        fields = VaccineCardShort.Meta.fields + (
            'revision_date',
            'pregnancy_status',
            'age_allowed',
            'administration_methods',
            'contraindications',
            'ingredients',
            'storage_conditions',
            'qr_code_url',
            'instruction_patient_url',
            'instruction_specialist_url',
        )

    def get_contraindications(self, obj):
        """Возвращает противопоказания."""
        if not obj.current_version:
            return {ContraindicationType.ABSOLUTE: [], ContraindicationType.TEMPORARY: []}

        contraindications = obj.current_version.contraindications_relations.select_related('contraindication')
        result = defaultdict(list)
        for item in contraindications:
            result[item.contraindication_type].append(item.contraindication.name)
        return dict(result)

    def get_ingredients(self, obj):
        """Возвращает ингредиенты."""
        if not obj.current_version:
            return {IngredientRoleType.ACTIVE: [], IngredientRoleType.AUXILIARY: []}
        ingredients = obj.current_version.ingredient_relations.select_related('ingredient')
        result = defaultdict(list)
        for item in ingredients:
            if item.role == IngredientRoleType.ACTIVE:
                result[IngredientRoleType.ACTIVE].append(item.ingredient.name)
            elif item.role == IngredientRoleType.AUXILIARY:
                result[IngredientRoleType.AUXILIARY].append(item.ingredient.name)
        return dict(result)

    def get_administration_methods(self, obj):
        """Возвращает способы введения."""
        if not obj.current_version:
            return []
        methods = obj.current_version.administration_method_relations.select_related('administration_method')
        return [
            {
                'method': item.administration_method.name,
                'age_from': item.age_from,
                'age_to': item.age_to,
            }
            for item in methods
        ]

    def get_age_allowed(self, obj):
        """Возвращает допустимый возрат."""
        if not obj.current_version:
            return 'не указано'
        min_age = obj.current_version.min_age
        max_age = obj.current_version.max_age
        if min_age and max_age and min_age % 12 == 0 and max_age % 12 == 0:
            min_years = min_age // 12
            max_years = max_age // 12
            if min_years == max_years:
                return format_age(min_age)
            return f'от {min_years} до {max_years} лет'
        if min_age and max_age:
            if min_age == max_age:
                return format_age(min_age)
            return f'от {format_age(min_age)} до {format_age(max_age)}'
        elif min_age:
            return f'от {format_age(min_age)}'
        elif max_age:
            return f'до {format_age(max_age)}'
        return 'не указано'
