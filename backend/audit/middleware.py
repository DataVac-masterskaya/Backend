from contextvars import ContextVar

from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse

User = get_user_model()
audit_context_var = ContextVar('audit_context', default=None)


def get_audit_context() -> tuple[User | None, str | None]:
    """
    Retrieves the current audit context (user and IP address).

    Returns:
        A tuple containing the user and IP address.
    """
    data = audit_context_var.get() or {}
    return (data.get('user'), data.get('ip_address'))


class AuditContextMiddleware:
    """
    Middleware for collecting user and IP address data.

    This middleware sets the user and IP address to the context variable
    before processing the request.
    """

    def __init__(self, get_response: callable) -> None:
        """
        Initialize the middleware.

        Args:
            get_response: The next callable in the middleware chain.
        """
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
        response = self.get_response(request)
        return response
