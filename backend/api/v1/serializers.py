# from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from reference_books.models import (
    Infection,
    Ingredients,
    MethodsOfAdministration,
)
from vaccines.models import VaccineCardVersion, VaccineCardVersionInfection


class SearchSelectSerializer(serializers.Serializer):
    """Сериализатор для фиксации выбора сущности в поиске."""

    ALLOWED_TYPES = ('infection', 'ingredient', 'contraindication', 'instruction', 'vaccineCard')

    entityType = serializers.CharField()
    entityId = serializers.IntegerField(min_value=1)

    def validate_entityType(self, value):
        """Проверяет что entityType входит в список допустимых типов."""
        if value not in self.ALLOWED_TYPES:
            raise serializers.ValidationError(f'Allowed types: {", ".join(self.ALLOWED_TYPES)}')
        return value

    class Meta:
        ref_name = 'ApiV1SearchSelect'


class SearchSelectResponseSerializer(serializers.Serializer):
    """Описывает ответ фиксации выбора сущности в поиске."""

    searchSelectCount = serializers.IntegerField()

    class Meta:
        ref_name = 'ApiV1SearchSelectResponse'


class InfectionSerializer(serializers.ModelSerializer):
    """Список инфекций."""

    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
    )

    class Meta:
        model = Infection
        fields = (
            'id',
            'name',
            'category',
            'popularity',
        )


class InfectionCartSerializer(InfectionSerializer):
    """Карточка инфекции."""

    vaccines = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Infection
        fields = (
            'id',
            'name',
            'category',
            'popularity',
            'vaccines',
        )

    def get_vaccines(self, obj):
        """Возвращает вакцины, связанные с инфекцией."""
        return VaccineCardVersion.objects.filter(
            id__in=VaccineCardVersionInfection.objects.filter(infection=obj).values('vaccine_card_version__id')
        ).values_list('name', flat=True)


class IngredientsSerializer(serializers.ModelSerializer):
    """Ингредиенты."""

    TYPE_CHOICES = [
        ('Адъювант', 'Адъювант'),
        ('Стабилизатор', 'Стабилизатор'),
        ('Консервант', 'Консервант'),
        ('Подсластитель', 'Подсластитель'),
        ('Эмульгатор', 'Эмульгатор'),
        ('Следы производства', 'Следы производства'),
    ]

    type = serializers.ChoiceField(choices=TYPE_CHOICES, error_messages={'invalid_choice': 'Неверный тип ингредиента'})

    class Meta:
        model = Ingredients
        fields = (
            'id',
            'name',
            'type',
            'popularity',
        )


class MethodsOfAdministrationSerializer(serializers.ModelSerializer):
    """Список способов введения."""

    # list_icon_url = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = MethodsOfAdministration
        fields = (
            'id',
            'name',
            'description',
            'list_icon_url',
            'note',
            'code',
        )


class MethodsOfAdministrationCartSerializer(serializers.ModelSerializer):
    """Карточка способа введения."""

    # detail_image_url = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = MethodsOfAdministration
        fields = (
            'id',
            'name',
            'description',
            'detail_image_url',
            'note',
            'code',
        )


'''class VaccineCardInstructionPatientSerializer(serializers.ModelSerializer):
    """Инструкция для неспециалистов"""

    # instruction_patient = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = VaccineCardVersion
        fields = (
            'nonspec_url',
        )

    # def get_instruction_patient(self, obj):
    #     """Возвращает инструкцию для неспециалистов."""
    #     return obj.published_version.nonspec_url'''
