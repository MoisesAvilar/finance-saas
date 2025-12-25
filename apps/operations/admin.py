from django.contrib import admin
from .models import DailyRecord, Maintenance, Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "color_display", "user")
    list_filter = ("type", "user")
    search_fields = ("name",)

    # Mostra a cor visualmente no admin
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
    list_filter = ("is_active", "date", "vehicle", "user")
    search_fields = ("vehicle__plate", "user__username")
    date_hierarchy = "date"
    readonly_fields = ("created_at", "updated_at")

    # Organiza os campos em seções
    fieldsets = (
        ("Status", {"fields": ("user", "vehicle", "date", "is_active")}),
        ("Rodagem", {"fields": ("start_km", "end_km")}),
        ("Financeiro (Consolidado)", {"fields": ("total_income", "total_cost")}),
        (
            "Metadados",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "date_display",
        "type",
        "category",
        "amount",
        "description",
        "record_link",
    )
    list_filter = ("type", "category", "created_at")
    search_fields = ("description", "category__name")

    def date_display(self, obj):
        return obj.created_at.strftime("%d/%m/%Y %H:%M")

    date_display.short_description = "Data/Hora"

    # Cria um link clicável para o Registro Diário pai
    def record_link(self, obj):
        from django.utils.html import format_html
        from django.urls import reverse

        url = reverse("admin:operations_dailyrecord_change", args=[obj.record.id])
        return format_html('<a href="{}">{}</a>', url, obj.record)

    record_link.short_description = "Registro Diário"


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ("date", "vehicle", "type", "cost", "odometer")
    list_filter = ("type", "vehicle", "date")
    search_fields = ("description", "vehicle__model_name")
    date_hierarchy = "date"
