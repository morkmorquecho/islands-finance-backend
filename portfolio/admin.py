from django.contrib import admin

from core.utils.admin import BaseAdmin
from .models import Island, IslandTemplate, Module


@admin.register(IslandTemplate)
class IslandTemplateAdmin(BaseAdmin):
    list_display = (
        "name",
        "kind",
        "symbol",
        "default_rate",
        "color",
    )

    search_fields = (
        "name",
        "symbol",
    )

    list_filter = (
        "kind",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Module)
class ModuleAdmin(BaseAdmin):
    list_display = (
        "name",
        "type",
        "user",
        "order",
    )

    search_fields = (
        "name",
        "user__email",
    )

    list_filter = (
        "type",
    )

    autocomplete_fields = (
        "user",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Island)
class IslandAdmin(BaseAdmin):
    list_display = (
        "name",
        "kind",
        "module",
        "user",
        "template",
        "currency",
        "symbol",
        "interest_type",
        "annual_rate",
        "color",
    )

    search_fields = (
        "name",
        "currency",
        "symbol",
        "module__name",
        "user__email",
        "template__name",
        "template__symbol",
    )

    list_filter = (
        "kind",
        "interest_type",
        "currency",
    )

    autocomplete_fields = (
        "module",
        "user",
        "template",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )