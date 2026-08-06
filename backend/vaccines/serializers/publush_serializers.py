from rest_framework import serializers

from vaccines.models import (
    VaccineCard,
)


class VaccineCardShort(serializers.ModelSerializer):
    """Сериализатор для краткой информации о карточке вакцины."""

    name = serializers.SerializerMethodField()
    official_name = serializers.SerializerMethodField()
    is_available_in_rf = serializers.SerializerMethodField()
    # min_age_days = serializers.IntegerField(source='current_version.min_age_days')
    # max_age_days = serializers.IntegerField(source='current_version.max_age_days')
    age_allowed = serializers.SerializerMethodField()
    pregnancy_usage_status = serializers.SerializerMethodField()
    infections = serializers.SerializerMethodField()
    administration_methods = serializers.SerializerMethodField()
    popularity = serializers.IntegerField()

    class Meta:
        model = VaccineCard
        fields = (
            'id',
            'name',
            'official_name',
            'is_available_in_rf',
            # 'min_age_days',
            # 'max_age_days',
            'age_allowed',
            'pregnancy_usage_status',
            'infections',
            'administration_methods',
            'popularity',
        )

    def get_infections(self, obj):
        if obj.current_version:
            return list(obj.current_version.infections.values('id', 'name'))
        return []

    def get_administration_methods(self, obj):
        if not obj.current_version:
            return []
        methods = obj.current_version.administration_method_relations.select_related('administration_method')
        return [
            {
                'code': item.administration_method.code,
                'age_group': None,
                'note': item.note,
            }
            for item in methods
        ]

    def get_name(self, obj):
        if obj.current_version and obj.current_version.name:
            return obj.current_version.name
        return 'Отсутствует название'

    def get_official_name(self, obj):
        if obj.current_version and obj.current_version.official_name:
            return obj.current_version.official_name
        return None

    def get_is_available_in_rf(self, obj):
        if obj.current_version:
            return obj.current_version.is_available_in_rf
        return False

    def get_age_allowed(self, obj):
        if obj.current_version and obj.current_version.age_allowed:
            return obj.current_version.age_allowed
        return None

    def get_pregnancy_usage_status(self, obj):
        if obj.current_version:
            return obj.current_version.pregnancy_usage_status
        return False


class VaccineCardDetail(VaccineCardShort):
    """Сериализатор для детального просмотра карточки вакцины."""

    revision_date = serializers.SerializerMethodField()
    nonspec_url = serializers.SerializerMethodField()
    instruction_url = serializers.SerializerMethodField()
    contraindications = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    manufacturer = serializers.SerializerMethodField()
    storage_conditions = serializers.SerializerMethodField()
    schedule_info = serializers.SerializerMethodField()
    side_effects = serializers.SerializerMethodField()
    indications = serializers.SerializerMethodField()
    interaction_info = serializers.SerializerMethodField()
    compatibility_info = serializers.SerializerMethodField()

    class Meta:
        model = VaccineCard
        fields = (
            'id',
            'name',
            'official_name',
            'is_available_in_rf',
            'revision_date',
            'nonspec_url',
            'instruction_url',
            # 'min_age_days',
            # 'max_age_days',
            'age_allowed',
            'pregnancy_usage_status',
            'infections',
            'administration_methods',
            'contraindications',
            'ingredients',
            'comment',
            'manufacturer',
            'storage_conditions',
            'schedule_info',
            'side_effects',
            'indications',
            'interaction_info',
            'compatibility_info',
        )

    def get_administration_methods(self, obj):
        if not obj.current_version:
            return []

        methods = obj.current_version.administration_method_relations.select_related('administration_method')
        return [
            {
                'code': item.administration_method.code,
                'age_group': item.age_group,
                'note': item.note,
            }
            for item in methods
        ]

    def get_contraindications(self, obj):
        if not obj.current_version:
            return []

        contraindications = obj.current_version.contraindications_relations.select_related('contraindication')
        return [
            {
                'id': item.contraindication.id,
                'name': item.contraindication.name,
                'type': item.contraindication_type,
            }
            for item in contraindications
        ]

    def get_ingredients(self, obj):
        if not obj.current_version:
            return []

        ingredients = obj.current_version.ingredient_relations.select_related('ingredient')
        return [
            {
                'id': item.ingredient.id,
                'name': item.ingredient.name,
                'role': item.role,
            }
            for item in ingredients
        ]

    def get_comment(self, obj):
        if not obj.current_version:
            return {'source': None, 'text': None}
        return {
            'source': obj.current_version.comment_source,
            'text': obj.current_version.comment_ANO,
        }

    def get_version_attr(self, obj, attr):
        """Возвращает поле current_version, либо None, если версии нет."""
        if obj.current_version:
            return getattr(obj.current_version, attr)
        return None

    def get_revision_date(self, obj):
        return self.get_version_attr(obj, 'revision_date')

    def get_nonspec_url(self, obj):
        return self.get_version_attr(obj, 'nonspec_url')

    def get_instruction_url(self, obj):
        return self.get_version_attr(obj, 'instruction_url')

    def get_manufacturer(self, obj):
        return self.get_version_attr(obj, 'manufacturer')

    def get_storage_conditions(self, obj):
        return self.get_version_attr(obj, 'storage_conditions')

    def get_schedule_info(self, obj):
        return self.get_version_attr(obj, 'schedule_info')

    def get_side_effects(self, obj):
        return self.get_version_attr(obj, 'side_effects')

    def get_indications(self, obj):
        return self.get_version_attr(obj, 'indications')

    def get_interaction_info(self, obj):
        return self.get_version_attr(obj, 'interaction_info')

    def get_compatibility_info(self, obj):
        return self.get_version_attr(obj, 'compatibility_info')
