from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Subscription

User = get_user_model()


# Не регистрируем User повторно, так как он уже зарегистрирован
# с UserAdmin в django.contrib.auth.admin
# @admin.register(User)
# class UserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'first_name', 'last_name')
#     list_filter = ('username', 'email')
#     search_fields = ('username', 'email')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user__username', 'author__username')
