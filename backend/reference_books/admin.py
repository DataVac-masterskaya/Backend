from django.contrib import admin

from reference_books.models import CategoryInfection, Infection, Ingredients, MethodsOfAdministration


@admin.register(CategoryInfection)
class CategoryInfectionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 20
    # list_editable = ('name',)
    ordering = ('name',)


@admin.register(Infection)
class InfectionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'category',
        'search_select_count',
        'search_weight',
    )
    search_fields = (
        'name',
        'category',
    )
    list_per_page = 20
    list_editable = (
        'name',
        'category',
        'search_weight',
    )
    ordering = ('name',)


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    """Ингредиенты."""

    list_display = (
        'id',
        'name',
        'type',
        'description',
        'search_select_count',
        'search_weight',
    )
    search_fields = (
        'name',
        'type',
        'description',
    )
    list_filter = (
        'name',
        'type',
    )
    list_per_page = 20
    ordering = ('name',)
    list_editable = ('description',)
    readonly_fields = ('id',)


@admin.register(MethodsOfAdministration)
class MethodsOfAdministrationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'description',
        'list_icon_url',
        'detail_image_url',
    )
    search_fields = ('name',)
    list_per_page = 20
    list_editable = (
        'name',
        'description',
        'list_icon_url',
        'detail_image_url',
    )
    ordering = ('name',)
