from django.apps import AppConfig


class InstructionsConfig(AppConfig):
    """Описывает настройки приложения справочника инструкций."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'instructions'
    verbose_name = 'Instructions'
