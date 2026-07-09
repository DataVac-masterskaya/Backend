from django.contrib import admin

from vaccines.models import VaccineCard, VaccineCardVersion


class VaccineCardVersionInline(admin.TabularInline):
    """Версии карточки."""

    model = VaccineCardVersion
    fields = ('version_number', 'version_status', 'name', 'official_name', 'created_at')
    readonly_fields = ('version_number', 'version_status', 'name', 'official_name', 'created_at')
    extra = 0
    can_delete = False
    ordering = ('-version_number',)
    verbose_name = 'Версия'
    verbose_name_plural = 'Версии'


@admin.register(VaccineCard)
class VaccineCardAdmin(admin.ModelAdmin):
    """Админка для карточки вакцины."""

    list_display = ('id', 'status', 'is_visible', 'created_at')
    list_filter = ('status', 'is_visible')
    search_fields = ('id', 'versions__name', 'versions__official_name')
    readonly_fields = ('id', 'created_at', 'updated_at', 'created_by', 'updated_by')
    inlines = [VaccineCardVersionInline]
