from django.contrib import admin
from .models import DailyRecord, Maintenance, Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
        "color_display",
        "user",
        "is_fuel",
        "is_maintenance",
    )
    list_filter = ("type", "is_fuel", "is_maintenance")
    search_fields = ("name", "user__username")

    def color_display(self, obj):
        from django.utils.html import format_html

        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 50%; border: 1px solid #ccc;"></div>',
            obj.color,
        )

    color_display.short_description = "Cor"


@admin.register(DailyRecord)
class DailyRecordAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "vehicle",
        "user",
        "km_driven",
        "total_income",
        "total_cost",
        "profit",
        "is_active",
    )
    list_filter = ("is_active", "date", "vehicle")
    search_fields = ("vehicle__plate", "user__username")
    date_hierarchy = "date"
    readonly_fields = ("created_at", "updated_at", "total_income", "total_cost")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date_display",
        "type",
        "category",
        "amount",
        "description",
        "created_at",
        "is_full_tank",
    )

    list_editable = ("amount", "description", "category", "is_full_tank")

    list_filter = ("type", "category", "is_full_tank", "created_at", "record__user")

    search_fields = (
        "description",
        "category__name",
        "record__user__username",
        "record__vehicle__model_name",
    )
    raw_id_fields = ("record", "category")

    fieldsets = (
        (
            "Dados Principais",
            {"fields": ("record", "type", "category", "amount", "description")},
        ),
        (
            "Detalhes de Combustível & Km",
            {
                "fields": ("liters", "is_full_tank", "actual_km", "next_due_km"),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadados",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    readonly_fields = ("updated_at",)

    def date_display(self, obj):
        return obj.created_at.strftime("%d/%m %H:%M")

    date_display.short_description = "Data"


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ("date", "vehicle", "type", "cost", "odometer")
    list_filter = ("type", "vehicle", "date")
    search_fields = ("description", "vehicle__model_name")
    date_hierarchy = "date"
    raw_id_fields = ("transaction", "vehicle", "user")
