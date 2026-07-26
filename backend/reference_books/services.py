from django.db import transaction

from vaccines.models import VaccineCardVersionIngredient


@transaction.atomic
def merge_ingredients(main, duplicates):
    """Объединяет несколько ингредиентов в один."""
    for duplicate in duplicates:
        if duplicate.pk == main.pk:
            continue

        (VaccineCardVersionIngredient.objects.filter(ingredient=duplicate).update(ingredient=main))

        duplicate.delete()
