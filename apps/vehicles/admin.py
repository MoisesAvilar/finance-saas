from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "model_name",
        "plate",
        "fuel_type",
        "initial_km",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "fuel_type", "created_at")
    search_fields = ("model_name", "plate", "user__username")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("is_active",)  # Permite ativar/desativar direto na lista

    fieldsets = (
        ("Identificação", {"fields": ("user", "model_name", "plate", "is_active")}),
        ("Detalhes Técnicos", {"fields": ("fuel_type", "initial_km")}),
        (
            "Metadados",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def save_model(self, request, obj, form, change):
        # Garante que a placa fique maiúscula ao salvar pelo Admin
        obj.plate = obj.plate.upper().replace("-", "").strip()
        super().save_model(request, obj, form, change)
