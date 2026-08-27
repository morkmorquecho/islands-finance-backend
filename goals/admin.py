from django.contrib import admin

from core.utils.admin import BaseAdmin
from .models import Goal, GoalCompletion


@admin.register(Goal)
class GoalAdmin(BaseAdmin):
    list_display = (
        "island",
        "user",
        "target_amount",
        "frequency_days",
        "start_date",
        "active",
    )

    search_fields = (
        "island__name",
        "user__email",
    )

    list_filter = (
        "active",
        "start_date",
    )

    autocomplete_fields = (
        "island",
        "user",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(GoalCompletion)
class GoalCompletionAdmin(BaseAdmin):
    list_display = (
        "goal",
        "expected_date",
        "completed_date",
        "actual_amount",
        "transaction",
        "completion_status",
    )

    search_fields = (
        "goal__island__name",
    )

    list_filter = (
        "expected_date",
        "completed_date",
    )

    autocomplete_fields = (
        "goal",
        "transaction",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "completion_status",
    )

    @admin.display(description="Estado")
    def completion_status(self, obj):
        return "Completado" if obj.completed_date else "Pendiente"