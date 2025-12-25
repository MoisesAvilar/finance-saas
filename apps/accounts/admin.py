from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Colunas da tabela
    list_display = (
        "username",
        "email",
        "full_name",
        "is_active",
        "date_joined",
        "last_login",
    )

    # Filtros laterais
    list_filter = ("is_active", "is_staff", "date_joined")

    # Barra de busca (busca por tudo)
    search_fields = ("username", "email", "first_name", "last_name")

    # Ordenação padrão (mais recentes primeiro)
    ordering = ("-date_joined",)

    # Método auxiliar para mostrar nome completo na lista
    def full_name(self, obj):
        return obj.get_full_name()

    full_name.short_description = "Nome Completo"
