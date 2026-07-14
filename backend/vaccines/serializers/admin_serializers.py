from django.db import transaction
from rest_framework import serializers

from contraindications.models import Contraindication
from reference_books.models import Infection, Ingredients, MethodsOfAdministration
from vaccines.constants import DEFAULT_VERSION
from vaccines.models import (
    ContraindicationType,
    IngredientRoleType,
    VaccineCard,
    VaccineCardStatus,
    VaccineCardVersion,
    VaccineCardVersionAdministrationMethod,
    VaccineCardVersionContraindication,
    VaccineCardVersionIngredient,
    VersionStatus,
)
from vaccines.utils import bulk_create_relations, validate_exists


class IngredientItemSerializer(serializers.Serializer):
    """Сериализатор для валидации ингредиента в составе вакцины."""

    ingredient_id = serializers.IntegerField()
    role = serializers.ChoiceField(choices=IngredientRoleType.choices, default=IngredientRoleType.ACTIVE)

    def validate_ingredient_id(self, value):
        """Проверяет существование ингредиента в БД."""
        return validate_exists(
            Ingredients,
            value,
            f'Ингредиент с ID {value} не найден',
        )


class ContraindicationItemSerializer(serializers.Serializer):
    """Сериализатор для валидации противопоказания."""

    contraindication_id = serializers.IntegerField()
    type = serializers.ChoiceField(
        choices=ContraindicationType.choices, default=ContraindicationType.ABSOLUTE, source='contraindication_type'
    )

    def validate_contraindication_id(self, value):
        """Проверяет существование противопоказания в БД."""
        return validate_exists(
            Contraindication,
            value,
            f'Противопоказание с ID {value} не найдено',
        )


class AdministrationMethodItemSerializer(serializers.Serializer):
    """Сериализатор для валидации способа введения."""

    administration_method_id = serializers.IntegerField()
    age_group = serializers.CharField(required=False, allow_blank=True)
    note = serializers.CharField(required=False, allow_blank=True)

    def validate_administration_method_id(self, value):
        """Проверяет существование метода введения в БД."""
        return validate_exists(
            MethodsOfAdministration,
            value,
            f'Метод введения с ID {value} не найден',
        )


class CommentSerializer(serializers.Serializer):
    """Сериализатор для комментария АНО."""

    source = serializers.CharField(required=False, allow_blank=True)
    text = serializers.CharField(required=False, allow_blank=True)


class AdminVaccinesCreatedSerializers(serializers.ModelSerializer):
    """Сериализатор для создания карточки вакцины."""

    infection_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Infection.objects.all(),
        required=False,
        allow_empty=True,
    )

    ingredients = IngredientItemSerializer(many=True, required=False, default=list)
    contraindications = ContraindicationItemSerializer(many=True, required=False, default=list)
    administration_methods = AdministrationMethodItemSerializer(many=True, required=False, default=list)
    comment = CommentSerializer(required=False)

    class Meta:
        model = VaccineCardVersion
        fields = (
            'name',
            'official_name',
            'description',
            'manufacturer',
            'is_available_in_rf',
            'min_age',
            'max_age',
            'pregnancy_usage_status',
            'storage_conditions',
            'interaction_info',
            'compatibility_info',
            'schedule_info',
            'side_effects',
            'indications',
            'registration_date',
            'revision_date',
            'ohlp_url',
            'nonspec_url',
            'instruction_url',
            'pdf_url',
            'infection_ids',
            'ingredients',
            'contraindications',
            'administration_methods',
            'comment',
        )

    @transaction.atomic
    def create(self, validated_data):
        """Создает карточку вакцины."""
        user = self.context['request'].user
        infection_ids = validated_data.pop('infection_ids', [])
        ingredients_data = validated_data.pop('ingredients', [])
        contraindications_data = validated_data.pop('contraindications', [])
        administration_methods_data = validated_data.pop('administration_methods', [])
        comment_data = validated_data.pop('comment', None)
        vaccine_card = VaccineCard.objects.create(
            status=VaccineCardStatus.DRAFT, is_visible=False, created_by=user, updated_by=user
        )
        if comment_data:
            validated_data['comment_source'] = comment_data.get('source', '')
            validated_data['comment_ANO'] = comment_data.get('text', '')
        version = VaccineCardVersion.objects.create(
            vaccine_card=vaccine_card,
            version_number=DEFAULT_VERSION,
            version_status=VersionStatus.DRAFT,
            created_by=user,
            **validated_data,
        )
        if infection_ids:
            version.infections.set(infection_ids)
        bulk_create_relations(
            version, VaccineCardVersionIngredient, ingredients_data, defaults={'role': IngredientRoleType.ACTIVE}
        )
        bulk_create_relations(
            version,
            VaccineCardVersionContraindication,
            contraindications_data,
            defaults={'contraindication_type': ContraindicationType.ABSOLUTE},
        )
        bulk_create_relations(
            version,
            VaccineCardVersionAdministrationMethod,
            administration_methods_data,
            defaults={
                'age_group': '',
                'note': '',
            },
        )
        vaccine_card.current_version = version
        vaccine_card.save(update_fields=['current_version', 'updated_at'])
        return version

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет карточку вакцины."""
        user = self.context['request'].user
        infection_ids = validated_data.pop('infection_ids', [])
        ingredients_data = validated_data.pop('ingredients', [])
        contraindications_data = validated_data.pop('contraindications', [])
        administration_methods_data = validated_data.pop('administration_methods', [])
        comment_data = validated_data.pop('comment', None)
        last_version = instance.versions.order_by('-version_number').first()
        next_version_number = (last_version.version_number + 1) if last_version else DEFAULT_VERSION
        if comment_data:
            validated_data['comment_source'] = comment_data.get('source', '')
            validated_data['comment_ANO'] = comment_data.get('text', '')
        new_version = VaccineCardVersion.objects.create(
            vaccine_card=instance,
            version_number=next_version_number,
            version_status=VersionStatus.DRAFT,
            created_by=user,
            parent_version=last_version,
            **validated_data,
        )
        if infection_ids:
            infections = Infection.objects.filter(id__in=infection_ids)
            new_version.infections.set(infections)
        bulk_create_relations(
            new_version, VaccineCardVersionIngredient, ingredients_data, defaults={'role': IngredientRoleType.ACTIVE}
        )
        bulk_create_relations(
            new_version,
            VaccineCardVersionContraindication,
            contraindications_data,
            defaults={'contraindication_type': ContraindicationType.ABSOLUTE},
        )
        bulk_create_relations(
            new_version,
            VaccineCardVersionAdministrationMethod,
            administration_methods_data,
            defaults={
                'age_group': '',
                'note': '',
            },
        )

        instance.current_version = new_version
        instance.updated_by = user
        instance.save(update_fields=['current_version', 'updated_by', 'updated_at'])
        return new_version


class VaccinesShortSerializers(serializers.ModelSerializer):
    """Сериализатор для получения короткой информации о версии вакцины."""

    class Meta:
        model = VaccineCardVersion
        fields = (
            'id',
            'version_number',
            'version_status',
            'name',
            'official_name',
        )


class AdminVaccinesDetailSerializers(serializers.ModelSerializer):
    """Сериализатор для получения детальной информации о карточки вакцины."""

    version = VaccinesShortSerializers(source='current_version', read_only=True)

    class Meta:
        model = VaccineCard
        fields = ('id', 'current_version', 'published_version', 'status', 'is_visible', 'version')


class AdminVaccineCreateResponseSerializer(serializers.ModelSerializer):
    """Сериализатор для ответа создания карточки вакцины."""

    current_version_id = serializers.IntegerField(source='current_version.id')

    class Meta:
        model = VaccineCard
        fields = ('id', 'current_version_id', 'status')
