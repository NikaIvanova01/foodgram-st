from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction

from recipes.models import Recipe, RecipeIngredient
from api.serializers.users import UserProfileSerializer
from api.serializers.ingredients import (
    RecipeIngredientReadSerializer,
    RecipeIngredientWriteSerializer,
)
from api.serializers.fields import Base64ImageField


User = get_user_model()


class RecipeReadSerializer(serializers.ModelSerializer):
    """Serializer for reading recipe details."""

    author = UserProfileSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, read_only=True, source="recipe_ingredients"
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        read_only_fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        fields = read_only_fields

    def _get_exists_relation(self, recipe_obj, relation_name):
        request = self.context.get("request")
        return (
            request
            and request.user.is_authenticated
            and getattr(recipe_obj, relation_name)
            .filter(user=request.user)
            .exists()
        )

    def get_is_favorited(self, recipe_obj):
        return self._get_exists_relation(recipe_obj, "favoriterecipes")

    def get_is_in_shopping_cart(self, recipe_obj):
        return self._get_exists_relation(recipe_obj, "shoppingcarts")


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Serializer for writing recipe details."""

    ingredients = RecipeIngredientWriteSerializer(many=True, required=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "ingredients",
            "image",
            "name",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, ingredients_data):
        if not ingredients_data:
            raise serializers.ValidationError(
                {"ingredients": "Cannot be empty."}
            )

        ingredient_ids = [item["ingredient"] for item in ingredients_data]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {"ingredients": "Cannot contain duplicates."}
            )

        return ingredients_data

    def validate(self, data):
        if self.instance and "ingredients" not in data:
            raise serializers.ValidationError(
                {"ingredients": "This field is required."}
            )
        return data

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_data["ingredient"],
                    amount=ingredient_data["amount"],
                )
                for ingredient_data in ingredients_data
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = super().create(validated_data)
        self._create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        instance.recipe_ingredients.all().delete()
        self._create_recipe_ingredients(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        return RecipeReadSerializer(recipe, context=self.context).data
