from pyexpat.errors import messages

from django.contrib import admin

# Register your models here.
from django.contrib import admin

from core.mixins import SoftDeleteAdminMixin
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.admin import UserAdmin


#======================================================= USER =============================================================
@admin.action(description="Desactivar usuarios seleccionados")
def deactivate_users(modeladmin, request, queryset):
    updated = queryset.filter(is_active=True).update(is_active=False)
    modeladmin.message_user(
        request,
        f"{updated} usuario(s) desactivado(s).",
        level=messages.SUCCESS,
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    actions = [deactivate_users]
    list_display = (
        "id",
        "username",
        "email",
        "is_active",
        "last_login",
        "date_joined",
    )
