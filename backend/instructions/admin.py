from django.contrib import admin

from instructions.models import OfficialInstruction
from instructions.parsing import check_official_instruction_update


@admin.register(OfficialInstruction)
class OfficialInstructionAdmin(admin.ModelAdmin):
    """Настраивает отображение официальных инструкций в Django Admin."""

    list_display = (
        'id',
        'title',
        'source',
        'url',
        'has_update',
        'last_checked_at',
        'search_select_count',
        'search_weight',
    )
    list_filter = ('source', 'has_update')
    ordering = ('title',)
    search_fields = ('title', 'url', 'source')
    readonly_fields = ('parsed_text', 'content_hash', 'last_checked_at')
    actions = ('check_for_updates', 'mark_as_reviewed')

    @admin.action(description='Проверить сейчас на обновления в источнике')
    def check_for_updates(self, request, queryset):
        """Синхронно сверяет выбранные инструкции с источником по клику из админки."""
        updated_count = 0
        error_count = 0
        for instruction in queryset:
            try:
                if check_official_instruction_update(instruction):
                    updated_count += 1
            except Exception:
                error_count += 1

        if updated_count:
            self.message_user(request, f'Найдены обновления: {updated_count} шт.')
        else:
            self.message_user(request, 'Обновлений не найдено.')
        if error_count:
            self.message_user(request, f'Не удалось проверить: {error_count} шт. Подробности в логах.', level='WARNING')

    @admin.action(description='Отметить как просмотренное')
    def mark_as_reviewed(self, request, queryset):
        updated = queryset.filter(has_update=True).update(has_update=False)
        self.message_user(request, f'Отмечено как просмотренное: {updated} шт.')
