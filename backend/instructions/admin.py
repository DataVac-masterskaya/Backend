from django.contrib import admin

from instructions.models import OfficialInstruction


@admin.register(OfficialInstruction)
class OfficialInstructionAdmin(admin.ModelAdmin):
    """Настраивает отображение официальных инструкций в Django Admin."""

    list_display = (
        'id',
        'title',
        'source',
        'url',
        'search_select_count',
        'search_weight',
    )
    list_filter = ('source',)
    ordering = ('title',)
    search_fields = ('title', 'url', 'source')
