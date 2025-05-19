from djoser.serializers import UserSerializer
from rest_framework import serializers

from recipes.models import User, Recipe
from api.serializers.fields import Base64ImageField


class UserProfileSerializer(UserSerializer):
    """Serializer for user profile"""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (*UserSerializer.Meta.fields, "is_subscribed", "avatar")

    def get_is_subscribed(self, user_profile):
        request = self.context.get("request")
        return (
            request is not None
            and not request.user.is_anonymous
            and request.user.is_authenticated
            and user_profile.followers.filter(user=request.user).exists()
        )

    def get_avatar(self, user_profile):
        if user_profile.avatar:
            return user_profile.avatar.url
        return None


class UserAvatarSerializer(serializers.ModelSerializer):
    """Serializer for user avatar"""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ("avatar",)

    def update(self, instance, validated_data):
        avatar = validated_data.get("avatar")
        if avatar is None:
            raise serializers.ValidationError("Avatar is required")

        instance.avatar = avatar
        instance.save()
        return instance


class RecipeShortSerializer(serializers.ModelSerializer):
    """Serializer for short recipe details."""

    class Meta:
        model = Recipe
        read_only_fields = ("id", "name", "image", "cooking_time")
        fields = read_only_fields


class UserWithRecipesSerializer(UserProfileSerializer):
    """Сериализатор для пользователя с его рецептами."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count", read_only=True
    )

    class Meta(UserProfileSerializer.Meta):
        fields = (
            *UserProfileSerializer.Meta.fields,
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, user_obj):
        return RecipeShortSerializer(
            user_obj.recipes.all()[
                : int(
                    self.context.get("request").GET.get(
                        "recipes_limit", 10**10
                    )
                )
            ],
            many=True,
        ).data
