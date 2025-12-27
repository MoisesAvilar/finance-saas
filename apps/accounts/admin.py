from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.db import models
from .models import CustomUser


class IsProFilter(admin.SimpleListFilter):
    title = "Plano"
    parameter_name = "is_pro"

    def lookups(self, request, model_admin):
        return (
            ("pro", "PRO"),
            ("free", "Grátis"),
        )

    def queryset(self, request, queryset):
        today = timezone.now().date()

        if self.value() == "pro":
            return queryset.filter(
                models.Q(is_superuser=True)
                | models.Q(pro_expiry_date__gte=today)
                | models.Q(is_pro_legacy=True)
            )

        if self.value() == "free":
            return queryset.filter(
                is_superuser=False, pro_expiry_date__lt=today, is_pro_legacy=False
            )

        return queryset


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "full_name",
        "is_pro",
        "pro_expiry_date",
        "is_active",
        "date_joined",
    )

    list_filter = (IsProFilter, "is_active", "is_staff", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)

    def full_name(self, obj):
        return obj.get_full_name()

    full_name.short_description = "Nome Completo"

    fieldsets = UserAdmin.fieldsets + (
        ("Assinatura", {"fields": ("pro_expiry_date", "is_pro_legacy")}),
    )
