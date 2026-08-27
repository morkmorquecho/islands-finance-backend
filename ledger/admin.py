from django.contrib import admin

from core.admin import BaseAdmin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(BaseAdmin):
    list_display = (
        "date",
        "type",
        "island",
        "user",
        "amount",
        "quantity",
        "price_at_tx",
        "category",
        "note",
    )

    search_fields = (
        "island__name",
        "user__email",
        "note",
    )

    list_filter = (
        "type",
        "category",
        "date",
    )

    autocomplete_fields = (
        "island",
        "user",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )