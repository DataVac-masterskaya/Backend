from reference_books.models import (
    Infection,
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
        # Заглушка
        # vaccines = Vaccines.objects.filter(infection=obj,)
        return ['vaccine1', 'vaccine2']
