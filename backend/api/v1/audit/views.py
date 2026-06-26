from rest_framework import mixins, viewsets  # noqa: I001
from rest_framework.permissions import IsAdminUser

from audit.models import AuditLog  # pyrefly: ignore [missing-import]
from .serializers import AuditLogSerializer


class AuditLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Эндпоинт для просмотра истории действий пользователей (аудит-лог)."""

    queryset = AuditLog.objects.select_related('user').all()
    permission_classes = (IsAdminUser,)
    serializer_class = AuditLogSerializer
    pagination_class = None
