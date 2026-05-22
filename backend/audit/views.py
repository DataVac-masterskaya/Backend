from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAdminUser

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for audit log.

    Attributes:
    - Uses select_related for optimizing user queries
    - Sorts by creation date in descending order (newest records first)
    - Pagination is implemented for large volumes of data
    - Uses SessionAuthentication (standard for admin panel)
    """

    queryset = AuditLog.objects.select_related('user').all()
    permission_classes = (IsAdminUser,)
    serializer_class = AuditLogSerializer
    pagination_class = None  # Или стандартная пагинация, если нужно
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('action_type', 'entity_type', 'entity_id', 'user_id')
