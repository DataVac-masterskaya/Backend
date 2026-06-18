from reference_books.models import (
    Infection,
    Ingredients,
    # Vaccines,
)
from rest_framework import serializers


class SearchSelectSerializer(serializers.Serializer):
    """Сериализатор для фиксации выбора сущности в поиске."""

    ALLOWED_TYPES = ('infection', 'ingredient', 'contraindication', 'instruction', 'vaccineCard')

    entityType = serializers.CharField()
    entityId = serializers.IntegerField()

    def validate_entityType(self, value):
        """Проверяет что entityType входит в список допустимых типов."""
        if value not in self.ALLOWED_TYPES:
            raise serializers.ValidationError(f"Allowed types: {', '.join(self.ALLOWED_TYPES)}")
        return value


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
        # Заглушка
        # vaccines = Vaccines.objects.filter(infection=obj,)
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
