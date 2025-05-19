from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Foodgram user model"""

    email = models.EmailField("Электронная почта", unique=True, max_length=254)
    first_name = models.CharField("Имя", max_length=150)
    last_name = models.CharField("Фамилия", max_length=150)
    avatar = models.ImageField(
        "Аватар", upload_to="avatars/", blank=True, null=True
    )
    username = models.CharField(
        "Никнейм",
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=(r"^[\w.@+-]+$"),
                message=(
                    "Имя пользователя может содержать только буквы, "
                    "цифры и знаки @/./+/-/_"
                ),
                code="invalid_username",
            )
        ],
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Subscription(models.Model):
    """Foodgram subscription model"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="authors",
        verbose_name="Автор",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="Подписчик",
    )

    class Meta:
        ordering = ("user",)
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscription"
            )
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"


class Recipe(models.Model):
    """Recipe model"""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="автор",
    )
    name = models.CharField("название", max_length=256)
    text = models.TextField(verbose_name="описание")
    ingredients = models.ManyToManyField(
        "ingredient",
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="ингредиенты",
    )
    cooking_time = models.PositiveIntegerField(
        "время приготовления (в минутах)",
        validators=[MinValueValidator(1)],
    )
    image = models.ImageField("изображение", upload_to="recipes/")

    class Meta:
        ordering = ("name",)
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient model"""

    name = models.CharField(
        "название",
        max_length=256,
    )
    measurement_unit = models.CharField(
        "единица измерения",
        max_length=256,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient",
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.measurement_unit}"


class RecipeIngredient(models.Model):
    """Many to many relationship between Recipe and Ingredient"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="ингредиент",
    )
    amount = models.PositiveIntegerField(
        "количество",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ("recipe", "ingredient")
        verbose_name = "ингредиент в рецепте"
        verbose_name_plural = "ингредиенты в рецепте"

    def __str__(self):
        return (
            f"{self.ingredient} - "
            f"{self.amount} {self.ingredient.measurement_unit}"
        )


class UserRecipeRelation(models.Model):
    """Model for user recipe relations"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="пользователь",
        related_name="%(class)ss",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="рецепт",
        related_name="%(class)ss",
    )

    class Meta:
        abstract = True
        ordering = ("user", "recipe")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_%(class)s"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.recipe}"


class FavoriteRecipe(UserRecipeRelation):
    """Model for favorite recipes"""

    class Meta(UserRecipeRelation.Meta):
        verbose_name = "избранный рецепт"
        verbose_name_plural = "избранные рецепты"


class ShoppingCart(UserRecipeRelation):
    """Model for shopping cart items"""

    class Meta(UserRecipeRelation.Meta):
        verbose_name = "рецепт в списке покупок"
        verbose_name_plural = "рецепты в списке покупок"
