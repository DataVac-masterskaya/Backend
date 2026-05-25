from rest_framework import mixins, viewsets  # noqa: I001
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser

from audit.models import AuditLog  # pyrefly: ignore [missing-import]
from .serializers import AuditLogSerializer


class AuditLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Вьюсет, который отдаёт список логов.

    Админ заходит в панель и видит всю историю.
    - select_related('user'), чтобы база не легла от кучи запросов.
    - Сортировка от новых к старым (самое свежее всегда сверху).
    - Пагинация (чтобы страница не грузилась полчаса, если логов накопится миллион).
    - Пускаем только админов! Обычным юзерам тут ловить нечего.
    """

    queryset = AuditLog.objects.select_related('user').all()
    permission_classes = (IsAdminUser,)
    serializer_class = AuditLogSerializer
    pagination_class = PageNumberPagination
