from django.apps import AppConfig


class SearchConfig(AppConfig):
    """Описывает настройки приложения глобального поиска."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'search'
    verbose_name = 'Search'
