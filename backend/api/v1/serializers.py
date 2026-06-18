# from drf_extra_fields.fields import Base64ImageField
from reference_books.models import (
    Infection,
    Ingredients,
    MethodsOfAdministration,
    # Vaccines,
)
from rest_framework import serializers


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
            'vaccines',
        )

    def get_vaccines(self, obj):
        """
        Возвращает вакцины, связанные с инфекцией.

        TODO: vaccines = Vaccines.objects.filter(infection=obj,)
        """
        return ['vaccine1', 'vaccine2']


class IngredientsSerializer(serializers.ModelSerializer):
    """Ингредиенты."""

    class Meta:
        model = Ingredients
        fields = (
            'id',
            'name',
            'type',
            'description',
        )


class MethodsOfAdministrationSerializer(serializers.ModelSerializer):
    """Список способов введения."""

    # list_icon_url = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = (MethodsOfAdministration,)
        fields = (
            'id',
            'name',
            'description',
            'list_icon_url',
        )


class MethodsOfAdministrationCartSerializer(serializers.ModelSerializer):
    """Карточка способа введения."""

    # detail_image_url = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = (MethodsOfAdministration,)
        fields = (
            'id',
            'name',
            'description',
            'detail_image_url',
        )
