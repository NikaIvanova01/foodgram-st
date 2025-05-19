from django.urls import path

from .views import redirect_short_link

app_name = "recipes"

urlpatterns = [
    path(
        "s/<int:recipe_id>/", redirect_short_link, name="short-link-redirect"
    ),
]
