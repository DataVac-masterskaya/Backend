from rest_framework import serializers

from vaccines.models import (
    VaccineCard,
)


class VaccineCardShort(serializers.ModelSerializer):
    """Сериализатор для краткой информации о карточке вакцины."""

    name = serializers.CharField(source='current_version.name')
    official_name = serializers.CharField(source='current_version.official_name')
    is_available_in_rf = serializers.BooleanField(source='current_version.is_available_in_rf')
    # min_age_days = serializers.IntegerField(source='current_version.min_age_days')
    # max_age_days = serializers.IntegerField(source='current_version.max_age_days')
    age_allowed = serializers.CharField(source='current_version.age_allowed')
    pregnancy_usage_status = serializers.BooleanField(source='current_version.pregnancy_usage_status')
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


class VaccineCardDetail(serializers.ModelSerializer):
    """Сериализатор для детального просмотра карточки вакцины."""

    name = serializers.CharField(source='current_version.name')
    official_name = serializers.CharField(source='current_version.official_name')
    is_available_in_rf = serializers.BooleanField(source='current_version.is_available_in_rf')
    revision_date = serializers.CharField(source='current_version.revision_date')
    nonspec_url = serializers.URLField(source='current_version.nonspec_url')
    instruction_url = serializers.URLField(source='current_version.instruction_url')
    # min_age_days = serializers.IntegerField(source='current_version.min_age_days')
    # max_age_days = serializers.IntegerField(source='current_version.max_age_days')
    age_allowed = serializers.CharField(source='current_version.age_allowed')
    pregnancy_usage_status = serializers.BooleanField(source='current_version.pregnancy_usage_status')
    infections = serializers.SerializerMethodField()
    administration_methods = serializers.SerializerMethodField()
    contraindications = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    manufacturer = serializers.CharField(source='current_version.manufacturer')
    storage_conditions = serializers.CharField(source='current_version.storage_conditions')
    schedule_info = serializers.CharField(source='current_version.schedule_info')
    side_effects = serializers.CharField(source='current_version.side_effects')
    indications = serializers.CharField(source='current_version.indications')
    interaction_info = serializers.CharField(source='current_version.interaction_info')
    compatibility_info = serializers.CharField(source='current_version.compatibility_info')

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

    def get_infections(self, obj):
        if obj.current_version:
            return list(
                obj.current_version.infections.values(
                    'id',
                    'name',
                )
            )
        return []

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
        return {
            'source': obj.current_version.comment_source,
            'text': obj.current_version.comment_ANO,
        }
