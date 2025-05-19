from djoser.views import UserViewSet as DjoserUserViewSet
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from api.pagination import SitePagination
from api.serializers.users import (
    UserProfileSerializer,
    UserAvatarSerializer,
    UserWithRecipesSerializer,
)
from recipes.models import User, Subscription


class UserViewSet(DjoserUserViewSet):
    """User viewset"""

    queryset = User.objects.all()
    pagination_class = SitePagination
    serializer_class = UserProfileSerializer
    permission_classes = [AllowAny]

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        return super().me(request)

    @action(
        methods=["put", "delete"],
        detail=False,
        url_path="me/avatar",
        permission_classes=[IsAuthenticated],
    )
    def avatar(self, request):
        current_user = request.user
        if request.method == "PUT":
            serializer = UserAvatarSerializer(
                current_user,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"avatar": current_user.avatar.url}, status=status.HTTP_200_OK
            )

        if current_user.avatar:
            current_user.avatar.delete()
            current_user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=UserWithRecipesSerializer,
        pagination_class=SitePagination,
    )
    def subscriptions(self, request):
        """Returns users that current user is subscribed to."""
        subscribed_users = User.objects.filter(
            authors__user=request.user
        ).prefetch_related("recipes")

        paginated_users = self.paginate_queryset(subscribed_users)
        serializer = self.get_serializer(paginated_users, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["post", "delete"],
        permission_classes=[IsAuthenticated],
        serializer_class=UserWithRecipesSerializer,
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        current_user = request.user

        if request.method == "POST":
            if current_user == author:
                raise ValidationError("Cannot subscribe to yourself")

            subscription, created = Subscription.objects.get_or_create(
                user=current_user, author=author
            )

            if not created:
                raise ValidationError(
                    "You are already subscribed to this user"
                )

            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        get_object_or_404(
            Subscription, user=current_user, author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
