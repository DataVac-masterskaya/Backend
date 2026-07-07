from django.contrib.auth import get_user_model  # noqa: I001
from rest_framework import serializers

# pyrefly: ignore [missing-import]
from audit.models import AuditLog

from typing import cast
from django.contrib.auth.models import AbstractUser

User = cast(type[AbstractUser], get_user_model())


class UserRefSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name')

    def get_full_name(self, user: User) -> str:
        return user.username


class AuditLogSerializer(serializers.ModelSerializer):
    user = UserRefSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = ('id', 'user', 'entity_type', 'entity_id', 'action_type', 'details', 'created_at')
