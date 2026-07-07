from django.contrib import admin

from contraindications.models import Contraindication, ContraindicationCategory


@admin.register(ContraindicationCategory)
class ContraindicationCategoryAdmin(admin.ModelAdmin):
    """Настраивает отображение категорий противопоказаний в Django Admin."""

    list_display = ('id', 'name')
    ordering = ('name',)
    search_fields = ('name',)


@admin.register(Contraindication)
class ContraindicationAdmin(admin.ModelAdmin):
    """Настраивает отображение противопоказаний в Django Admin."""

    filter_horizontal = ('categories',)
    list_display = ('id', 'old_id', 'name', 'search_select_count', 'search_weight')
    list_filter = ('categories',)
    ordering = ('name',)
    search_fields = ('name',)
