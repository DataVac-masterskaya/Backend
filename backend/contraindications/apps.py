from django.apps import AppConfig


class ContraindicationsConfig(AppConfig):
    """Описывает настройки приложения справочника противопоказаний."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'contraindications'
    verbose_name = 'Contraindications'
