from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views.users import UserViewSet
from api.views.ingredients import IngredientViewSet
from api.views.recipes import RecipeViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="users")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")


urlpatterns = [
    path("auth/", include("djoser.urls.authtoken")),
    path("", include(router.urls)),
]
