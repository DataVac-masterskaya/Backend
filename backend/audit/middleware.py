from contextvars import ContextVar

from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse

User = get_user_model()
audit_context_var = ContextVar('audit_context', default=None)


def get_audit_context() -> tuple[User | None, str | None]:
    """
    Достает юзера и IP из контекста.

    Вытаскивает из специального хранилища (контекста)
    текущего юзера и его IP-адрес.
    Удобно, чтобы не тащить их через всю цепочку вызовов руками.
    """
    data = audit_context_var.get() or {}
    return (data.get('user'), data.get('ip_address'))


class AuditContextMiddleware:
    """
    Эта мидлварь ловит юзера и его IP-адрес.

    при каждом запросе и сохраняет в контекст.
    Нужно, чтобы наши сигналы потом знали, кто именно совершил действие.
    """

    def __init__(self, get_response: callable) -> None:
        """Конструктор мидлвари, запоминает функцию перехода к следующему шагу."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        audit_context_var.set(
            {
                'user': request.user,
                'ip_address': ip_address,
            }
        )
        return self.get_response(request)
