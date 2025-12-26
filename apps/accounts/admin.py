from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "full_name",
        "is_pro",
        "is_active",
        "date_joined",
    )

    list_filter = ("is_pro", "is_active", "is_staff", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)

    def full_name(self, obj):
        return obj.get_full_name()

    full_name.short_description = "Nome Completo"

    fieldsets = UserAdmin.fieldsets + (("Assinatura / Plano", {"fields": ("is_pro",)}),)
