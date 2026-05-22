from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver

from .middleware import get_audit_context
from .models import AuditLog

User = get_user_model()


class AuditLogger:
    @staticmethod
    def log_action(
        action_type: str, entity_type: str, entity_id: int | None = None, details: dict | None = None
    ) -> None:
        user, ip_address = get_audit_context()
        if user and not user.is_authenticated:
            user = None
        AuditLog.objects.create(
            user=user,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
        )


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs) -> None:  # noqa: D103
    AuditLogger.log_action('login', 'user', user.id)


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs) -> None:  # noqa: D103
    details = {'attempted_login': credentials.get('username')}
    AuditLogger.log_action('login_failed', 'user', details=details)


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs) -> None:  # noqa: D103
    if created:
        AuditLogger.log_action('user_create', 'user', instance.id)
    else:
        pass
        # Жду остальных что бы дополнить эту часть кода


# @receiver(post_save, sender='vaccines.VaccineCard')
# @staticmethod
# def log_vaccine_card_changes(sender, instance, created, **kwargs) -> None:
#     # Дождаться feat/vaccines и свериться с ним в плане названий.
#     # Использую vaccines.VaccineCard, так как на момент создания
#     # models.py в vaccines еще не существовало.
#     action = 'card_create' if created else 'card_update'
#     AuditLogger.log_action(action, 'vaccineCard', instance.id)
