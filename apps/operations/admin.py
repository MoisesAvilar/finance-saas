from django.contrib import admin
from django.utils.html import format_html
from .models import DailyRecord, Maintenance, Category, Transaction

admin.site.site_header = "DriverFinance Admin"
admin.site.site_title = "Portal Administrativo"
admin.site.index_title = "Gerenciamento do Sistema"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
        "color_display",
        "user",
        "is_fuel",
        "is_maintenance",
        "created_at",
        "updated_at",
    )
    list_filter = ("type", "is_fuel", "is_maintenance", "created_at", "updated_at", "user")
    search_fields = ("name", "user__username", "user__email")
    autocomplete_fields = ["user"]

    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 50%; border: 1px solid #ccc; box-shadow: 0 1px 2px rgba(0,0,0,0.1);"></div>',
            obj.color,
        )

    color_display.short_description = "Cor"


@admin.register(DailyRecord)
class DailyRecordAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "user",
        "vehicle",
        "km_driven_display",
        "financial_summary",
        "is_active",
    )
    list_filter = ("is_active", "date", "vehicle__model_name")
    search_fields = ("vehicle__plate", "user__username", "user__email")
    date_hierarchy = "date"
    autocomplete_fields = ["user", "vehicle"]
    readonly_fields = ("created_at", "updated_at", "total_income", "total_cost")

    def km_driven_display(self, obj):
        return f"{obj.km_driven} km"

    km_driven_display.short_description = "Rodagem"

    def financial_summary(self, obj):
        color = "green" if obj.profit >= 0 else "red"
        icon = "▲" if obj.profit >= 0 else "▼"
        return format_html(
            'Rec: R$ {} | Desp: R$ {} <br> <b>Res: <span style="color: {};">{} R$ {}</span></b>',
            obj.total_income,
            obj.total_cost,
            color,
            icon,
            obj.profit,
        )

    financial_summary.short_description = "Resumo Financeiro"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date_display",
        "type_colored",
        "category",
        "amount",
        "description",
        "is_full_tank",
        "record_link",
        "created_at",
        "updated_at",
    )
    list_editable = ("amount", "description", "category", "is_full_tank")
    list_filter = ("type", "category", "is_full_tank", "created_at", "record__user")
    search_fields = (
        "description",
        "category__name",
        "record__user__username",
        "record__vehicle__model_name",
    )
    autocomplete_fields = ["record", "category"]

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

    readonly_fields = ("created_at", "updated_at")

    def date_display(self, obj):
        return obj.created_at.strftime("%d/%m %H:%M")

    date_display.short_description = "Data"

    def type_colored(self, obj):
        color = "green" if obj.type == "INCOME" else "red"
        label = "Receita" if obj.type == "INCOME" else "Despesa"
        return format_html('<b style="color: {};">{}</b>', color, label)

    type_colored.short_description = "Tipo"

    def record_link(self, obj):
        return format_html(
            '<a href="/admin/operations/dailyrecord/{}/change/">Ver Registro</a>',
            obj.record.id,
        )

    record_link.short_description = "Jornada"


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ("date", "vehicle", "type", "cost", "status_display", "next_due_km")
    list_filter = ("type", "vehicle", "date")
    search_fields = ("title", "description", "vehicle__plate", "user__username")
    date_hierarchy = "date"
    autocomplete_fields = ["user", "vehicle", "transaction"]

    def status_display(self, obj):
        if not obj.next_due_km:
            return "-"

        current_km = (
            obj.vehicle.current_odometer
            if hasattr(obj.vehicle, "current_odometer")
            else 0
        )
        diff = obj.next_due_km - current_km

        if diff < 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">VENCIDA ({} km)</span>',
                abs(diff),
            )
        elif diff < 1000:
            return format_html(
                '<span style="color: orange; font-weight: bold;">Faltam {} km</span>',
                diff,
            )
        return format_html('<span style="color: green;">Em dia</span>')

    status_display.short_description = "Status"
