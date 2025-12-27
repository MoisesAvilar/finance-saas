from django.contrib import admin
from .models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "position", "active", "show_clicks", "created_at")
    readonly_fields = ("clicks",)

    def show_clicks(self, obj):
        return obj.clicks

    show_clicks.short_description = "Cliques Totais"
