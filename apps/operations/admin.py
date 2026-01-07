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
        "date_display",
        "type",
        "category",
        "amount",
        "is_full_tank",
        "description",
    )
    list_filter = ("type", "is_full_tank", "category", "created_at")
    search_fields = ("description", "category__name", "record__user__username")
    raw_id_fields = ("record", "category")

    def date_display(self, obj):
        return obj.created_at.strftime("%d/%m/%Y %H:%M")

    date_display.short_description = "Data/Hora"


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ("date", "vehicle", "type", "cost", "odometer")
    list_filter = ("type", "vehicle", "date")
    search_fields = ("description", "vehicle__model_name")
    date_hierarchy = "date"
    raw_id_fields = ("transaction", "vehicle", "user")
