from django.shortcuts import redirect
from django.core.exceptions import ValidationError

from .models import Recipe


def redirect_short_link(request, recipe_id):
    """Redirects to the recipe"""
    if not Recipe.objects.filter(id=recipe_id).exists():
        raise ValidationError(f"Рецепт с id={recipe_id} не существует")
    return redirect(f"/recipes/{recipe_id}/")
