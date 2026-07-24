from django import forms

from reference_books.models import Ingredients


class MergeIngredientsForm(forms.Form):
    main = forms.ModelChoiceField(
        queryset=Ingredients.objects.all(),
        label='Основной ингредиент',
    )

    duplicates = forms.ModelMultipleChoiceField(
        queryset=Ingredients.objects.all(),
        label='Объединить с',
    )
