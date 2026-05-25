from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .middleware import get_audit_context
from .models import ACTION_CHOICES, AuditLog

User = get_user_model()


class AuditLogger:
    """
    Специальный класс-помощник.

    Собирает данные и создаёт лог в базе.
    """

    @staticmethod
    def log_action(
        action_type: str, entity_type: str, entity_id: int | None = None, details: str | None = None
    ) -> None:
        """
        Сам метод, который собирает контекст (юзера и IP).

        И пишет готовую запись в БД.
        """
        user, ip_address = get_audit_context()
        if user and not user.is_authenticated:
            user = None
        full_details = details or ''
        if ip_address:
            full_details = f'{full_details} [IP: {ip_address}]'.strip()
        AuditLog.objects.create(
            user=user,
            entity_type=entity_type,
            entity_id=entity_id,
            action_type=action_type,
            details=full_details,
        )


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs) -> None:
    """
    Сигнал успешного входа.

    Ловит момент, когда кто-то успешно залогинился,
    и пишет об этом лог.
    """
    AuditLogger.log_action('login', 'user', user.id, details=ACTION_CHOICES['login'])


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs) -> None:
    """
    Сигнал неудачного входа.

    Ловит подозрительные/неудачные попытки входа
    и записывает, кого именно пытались взломать.
    """
    attempted_login = credentials.get('username') or 'не указан'
    details = f'{ACTION_CHOICES["login_failed"]} Пользователь: {attempted_login}'
    AuditLogger.log_action('login_failed', 'user', details=details)


@receiver(pre_save, sender=User)
def track_user_blocking_before_save(sender, instance, **kwargs) -> None:
    """
    Pre-save отслеживание блокировки.

    Сравнивает состояние юзера до сохранения в базу,
    чтобы понять, изменился ли статус активности (is_active).
    Если изменился - вешает временную метку на объект.
    """
    if instance.pk:
        old_user = User.objects.filter(pk=instance.pk).first()
        if old_user:
            instance._is_active_changed = old_user.is_active != instance.is_active


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs) -> None:
    """
    Post-save логирование создания/изменения.

    Записывает в аудит создание нового пользователя
    или факт его блокировки/разблокировки.
    Ориентируется на метки, которые были подготовлены на этапе pre_save.
    """
    if created:
        AuditLogger.log_action('user_create', 'user', instance.id, details=ACTION_CHOICES['user_create'])
    else:
        if getattr(instance, '_is_active_changed', False):
            action = 'block'
            details = {'is_active': instance.is_active, 'status': 'blocked' if not instance.is_active else 'active'}
            AuditLogger.log_action(action, 'user', instance.id, details)
        # Жду остальных что бы дополнить эту часть кода


# @receiver(post_save, sender='vaccines.VaccineCard')
# @staticmethod
# def log_vaccine_card_changes(sender, instance, created, **kwargs) -> None:
#     # Дождаться feat/vaccines и свериться с ним в плане названий.
#     # Использую vaccines.VaccineCard, так как на момент создания
#     # models.py в vaccines еще не существовало.
#     action = 'card_create' if created else 'card_update'
#     AuditLogger.log_action(action, 'vaccineCard', instance.id)
