from django.contrib import admin

from core.utils.admin import BaseAdmin

from .models import (
    TelegramLink,
    TelegramLinkCode,
    PendingTransaction,
    TelegramUpdate,
)


@admin.register(TelegramLink)
class TelegramLinkAdmin(BaseAdmin):
    list_display = (
        "user",
        "chat_id",
        "telegram_username",
        "default_island",
        "created_at",
    )
    search_fields = (
        "user__email",
        "telegram_username",
        "chat_id",
    )
    list_select_related = (
        "user",
        "default_island",
    )
    autocomplete_fields = (
        "user",
        "default_island",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(TelegramLinkCode)
class TelegramLinkCodeAdmin(BaseAdmin):
    list_display = (
        "user",
        "expires_at",
        "used_at",
        "created_at",
    )
    search_fields = (
        "user__email",
    )
    list_filter = (
        "expires_at",
        "used_at",
    )
    list_select_related = ("user",)
    autocomplete_fields = ("user",)
    readonly_fields = (
        "code_hash",
        "expires_at",
        "used_at",
        "created_at",
        "updated_at",
    )


@admin.register(PendingTransaction)
class PendingTransactionAdmin(BaseAdmin):
    list_display = (
        "type",
        "amount",
        "island",
        "link",
        "category",
        "date",
        "status",
        "expires_at",
        "confirmed_at",
    )
    search_fields = (
        "link__user__email",
        "link__telegram_username",
        "note",
        "category",
    )
    list_filter = (
        "status",
        "type",
        "date",
        "expires_at",
    )
    list_select_related = (
        "link",
        "link__user",
        "island",
        "transaction",
    )
    autocomplete_fields = (
        "link",
        "island",
        "transaction",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "confirmed_at",
    )
    date_hierarchy = "date"


@admin.register(TelegramUpdate)
class TelegramUpdateAdmin(BaseAdmin):
    list_display = (
        "update_id",
        "created_at",
    )
    search_fields = (
        "update_id",
    )
    readonly_fields = (
        "update_id",
        "created_at",
        "updated_at",
    )