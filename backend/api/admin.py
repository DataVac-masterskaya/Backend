from django.contrib import admin
from reference_books.models import Category, Infection


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class InfectionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'search_select_count',
        'search_weight',
    )
    search_fields = (
        'name',
        'category',
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Infection, InfectionAdmin)
