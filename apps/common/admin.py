from django.contrib import admin
from .models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "position", "active", "show_clicks", "created_at")
    list_filter = ("active", "position", "created_at")
    readonly_fields = ("clicks", "created_at", "updated_at")
    search_fields = ("title", "link")

    def show_clicks(self, obj):
        return obj.clicks

    show_clicks.short_description = "Cliques Totais"
