from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin

from .models import (
    User,
    Subscription,
    Ingredient,
    Recipe,
    RecipeIngredient,
    FavoriteRecipe,
    ShoppingCart,
)


class RecipesCountMixin:
    """Mixin providing recipes count functionality"""

    @admin.display(description="рецепты")
    def get_recipes_count(self, obj):
        return obj.recipes.count()


class BaseHasFilter(admin.SimpleListFilter):
    lookups_choices = (
        ("yes", "Есть"),
        ("no", "Нет"),
    )

    def lookups(self, request, model_admin):
        return self.lookups_choices

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(
                **{f"{self.field}__isnull": False}
            ).distinct()
        if self.value() == "no":
            return queryset.filter(**{f"{self.field}__isnull": True})


class HasRecipesFilter(BaseHasFilter):
    title = "наличие рецептов"
    parameter_name = "has_recipes"
    field = "recipes"
    lookups_choices = (
        ("yes", "Есть рецепты"),
        ("no", "Нет рецептов"),
    )


class HasFollowersFilter(BaseHasFilter):
    title = "наличие подписчиков"
    parameter_name = "has_followers"
    field = "authors"
    lookups_choices = (
        ("yes", "Есть подписчики"),
        ("no", "Нет подписчиков"),
    )


class HasSubscriptionsFilter(BaseHasFilter):
    title = "наличие подписок"
    parameter_name = "has_subscriptions"
    field = "followers"
    lookups_choices = (
        ("yes", "Есть подписки"),
        ("no", "Нет подписок"),
    )


@admin.register(User)
class SiteUserAdmin(UserAdmin, RecipesCountMixin):
    """Custom user admin class"""

    list_display = (
        "id",
        "username",
        "get_full_name",
        "email",
        "get_avatar",
        "get_recipes_count",
        "get_number_of_following",
        "get_number_of_followers",
    )
    list_filter = (
        HasRecipesFilter,
        HasFollowersFilter,
        HasSubscriptionsFilter,
        "is_active",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("id",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Персональная информация",
            {"fields": ("username", "first_name", "last_name", "avatar")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    @admin.display(description="ФИО")
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description="Аватар")
    @mark_safe
    def get_avatar(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" width="50" height="50" />'
        return ""

    @admin.display(description="подписчики")
    def get_number_of_followers(self, user_obj):
        return user_obj.authors.count()

    @admin.display(description="подписки")
    def get_number_of_following(self, user_obj):
        return user_obj.followers.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Subscription admin class"""

    list_display = ("id", "author", "user")
    list_filter = ("author", "user")
    search_fields = ("author__username", "user__username")


class CookingTimeFilter(admin.SimpleListFilter):
    """Filter recipes by cooking time with dynamic thresholds"""

    title = "время приготовления"
    parameter_name = "cooking_time"
    _thresholds = None

    def lookups(self, request, model_admin):
        cooking_times = [r.cooking_time for r in Recipe.objects.all()]
        if not cooking_times:
            return []

        min_time = min(cooking_times)
        max_time = max(cooking_times)

        if max_time - min_time <= 5:
            return []

        time_range = max_time - min_time
        self._thresholds = (
            min_time + time_range // 3,
            min_time + (2 * time_range) // 3,
        )
        threshold1, threshold2 = self._thresholds

        quick = medium = long = 0
        for t in cooking_times:
            if t < threshold1:
                quick += 1
            elif t < threshold2:
                medium += 1
            else:
                long += 1

        return [
            ("quick", f"до {threshold1} мин ({quick})"),
            ("medium", f"от {threshold1} до {threshold2} мин ({medium})"),
            ("long", f"от {threshold2} мин и больше ({long})"),
        ]

    def queryset(self, request, queryset):
        if not self.value() or not self._thresholds:
            return queryset

        threshold1, threshold2 = self._thresholds

        if self.value() == "quick":
            return queryset.filter(cooking_time__lte=threshold1)
        if self.value() == "medium":
            return queryset.filter(
                cooking_time__gt=threshold1, cooking_time__lte=threshold2
            )
        if self.value() == "long":
            return queryset.filter(cooking_time__gt=threshold2)
        return queryset


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Recipe admin model"""

    list_display = (
        "id",
        "name",
        "cooking_time",
        "author",
        "get_favorites_count",
        "get_ingredients",
        "get_image",
    )
    search_fields = (
        "name",
        "author__username",
        "author__first_name",
        "author__last_name",
    )
    list_filter = (CookingTimeFilter, "author")
    inlines = (RecipeIngredientInline,)

    @admin.display(description="в избранном")
    def get_favorites_count(self, obj):
        return obj.favoriterecipes.count()

    @admin.display(description="ингредиенты")
    @mark_safe
    def get_ingredients(self, obj):
        return "<br>".join(
            [
                f"{item.ingredient.name} - "
                f"{item.amount} "
                f"{item.ingredient.measurement_unit}"
                for item in obj.recipe_ingredients.all()
            ]
        )

    @admin.display(description="изображение")
    @mark_safe
    def get_image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100">'
        return "Нет изображения"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin, RecipesCountMixin):
    """Ingredient admin model"""

    list_display = ("name", "measurement_unit", "get_recipes_count")
    search_fields = ("name", "measurement_unit")
    list_filter = ("measurement_unit",)


@admin.register(FavoriteRecipe, ShoppingCart)
class UserRecipeRelationAdmin(admin.ModelAdmin):
    """Admin model for user-recipe relations"""

    list_display = ("user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user", "recipe")
