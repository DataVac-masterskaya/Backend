from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class TokenObtainPairSerializer(TokenObtainPairSerializer):
    """Сериализатор с расширенным ответом."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'full_name': self.user.full_name,
            'role': self.user.role,
        }
        return data


class AuthUserResponseSerializer(serializers.Serializer):
    """Схема краткой информации о пользователе внутри токена."""

    id = serializers.IntegerField(help_text='ID пользователя')
    full_name = serializers.CharField(help_text='Полное имя')
    role = serializers.CharField(help_text='Роль: admin|moderator')


class TokenPairResponseSerializer(serializers.Serializer):
    """Схема успешного ответа аутентификации (200 OK)."""

    access = serializers.CharField(help_text='JWT access токен')
    refresh = serializers.CharField(help_text='JWT refresh токен')
    user = AuthUserResponseSerializer()
