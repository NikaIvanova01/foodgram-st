from datetime import datetime
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.http import Http404, FileResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend


from recipes.models import Recipe, FavoriteRecipe, ShoppingCart
from api.serializers.recipes import (
    RecipeReadSerializer,
    RecipeWriteSerializer,
)
from api.serializers.users import RecipeShortSerializer
from api.permissions import IsAuthorOrReadOnly
from api.pagination import SitePagination
from api.filters import RecipeFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    pagination_class = SitePagination
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=["get"], detail=True, url_path="get-link")
    def get_link_to_recipe(self, request, pk):
        if not Recipe.objects.filter(pk=pk).exists():
            raise Http404

        return Response(
            {
                "short-link": request.build_absolute_uri(
                    reverse("recipes:short-link-redirect", args=[pk])
                )
            }
        )

    def _handle_recipe_relation(
        self, request, recipe_id, model_class, already_exists_message
    ):
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        current_user = request.user

        if request.method == "POST":
            _, created = model_class.objects.get_or_create(
                user=current_user, recipe=recipe
            )

            if not created:
                raise ValidationError({"errors": already_exists_message})

            return Response(
                RecipeShortSerializer(recipe).data,
                status=status.HTTP_201_CREATED,
            )

        get_object_or_404(
            model_class, user=current_user, recipe=recipe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self._handle_recipe_relation(
            request, pk, FavoriteRecipe, "Рецепт уже в избранном"
        )

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        return self._handle_recipe_relation(
            request, pk, ShoppingCart, "Рецепт уже в списке покупок"
        )

    @action(
        detail=False, permission_classes=[IsAuthenticated], methods=["get"]
    )
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(shoppingcarts__user=request.user)

        if not recipes.exists():
            raise ValidationError({"errors": "Список покупок пуст"})

        ingredients = (
            recipes.values(
                "ingredients__name", "ingredients__measurement_unit"
            )
            .annotate(total_amount=Sum("recipe_ingredients__amount"))
            .order_by("ingredients__name")
        )

        current_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        shopping_list = [
            "Фудграм - Список покупок",
            f"Дата: {current_date} UTC",
            f"Пользователь: {request.user.username}",
            "",
            "Ингредиенты:",
        ]

        for i, ingredient in enumerate(ingredients, 1):
            shopping_list.append(
                f"{i}. {ingredient['ingredients__name'].title()} - "
                f"{ingredient['total_amount']} "
                f"{ingredient['ingredients__measurement_unit']}"
            )

        shopping_list.append("")
        shopping_list.append("Рецепты:")

        for recipe in recipes:
            shopping_list.append(
                f"- {recipe.name} (автор: {recipe.author.get_full_name()})"
            )

        shopping_list.append("")
        shopping_list.append(
            f"Фудграм - Ваш кулинарный помощник © {datetime.now().year}"
        )

        return FileResponse(
            ("\n".join(shopping_list)),
            as_attachment=True,
            filename="shopping_list.txt",
            content_type="text/plain; charset=utf-8",
        )
