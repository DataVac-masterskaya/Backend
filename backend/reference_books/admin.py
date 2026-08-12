from django.contrib import admin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path

from reference_books.forms import MergeIngredientsForm
from reference_books.models import CategoryInfection, Infection, Ingredients, MethodsOfAdministration
from reference_books.services import merge_ingredients


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

    def get_urls(self):
        urls = super().get_urls()

        my_urls = [
            path(
                'merge/',
                self.admin_site.admin_view(self.merge_view),
                name='reference_books_ingredients_merge',
            ),
        ]

        return my_urls + urls

    def merge_view(self, request):
        if request.method == 'POST':
            form = MergeIngredientsForm(request.POST)
            if form.is_valid():
                main = form.cleaned_data['main']
                duplicates = form.cleaned_data['duplicates']
                if main in duplicates:
                    form.add_error(None, 'Основной ингредиент нельзя объединять сам с собой.')
                merge_ingredients(main, duplicates)
                self.message_user(request, 'Ингредиенты успешно объединены.')

                return redirect('../')
        else:
            form = MergeIngredientsForm()
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'title': 'Объединение ингредиентов',
            'form': form,
        }

        return TemplateResponse(
            request,
            'admin/reference_books/merge_ingredients.html',
            context,
        )


@admin.register(MethodsOfAdministration)
class MethodsOfAdministrationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'code',
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
