from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Доступ для Администратора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsModerator(BasePermission):
    """Доступ для Модератора."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator
