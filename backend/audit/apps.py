from django.apps import AppConfig


class AuditConfig(AppConfig):
    """Configuration class for the audit app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit'

    def ready(self) -> None:
        from . import signals  # noqa: F401
