from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import AuditLog

User = get_user_model()


class UserRefSerializer(serializers.ModelSerializer):
    """Serializer for non-admin users used in audit logs."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        # добавить необходимые поля (если будет нужно в будущем)


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs."""

    user = UserRefSerializer(read_only=True)

    class Meta:
        model = AuditLog
        exclude = ('ip_address',)
