from django.contrib.auth import get_user_model  # noqa: I001
from rest_framework import serializers

# pyrefly: ignore [missing-import]
from audit.models import AuditLog

User = get_user_model()


class UserRefSerializer(serializers.ModelSerializer):
    """
    Сериализатор для user.

    Превращает юзера в красивый JSON с id и именем,
    чтобы в логах было понятно, кто именно накосячил.
    """

    fullName = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'fullName')

    def get_fullName(self, obj: User) -> str:
        return obj.get_full_name() or obj.username


class AuditLogSerializer(serializers.ModelSerializer):
    """Главный сериализатор для логов аудита.

    Переводит всю запись из базы в JSON,
    чтобы фронтендеры могли нарисовать таблицу.
    """

    user = UserRefSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = ('id', 'user', 'entity_type', 'entity_id', 'action_type', 'details', 'created_at')
