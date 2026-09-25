from django.contrib import admin
from .models import WasteItem, WasteEntry


@admin.register(WasteItem)
class WasteItemAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "cost_per_unit", "location", "is_active")
    list_filter = ("location", "is_active")
    search_fields = ("name",)
    list_editable = ("is_active",)


@admin.register(WasteEntry)
class WasteEntryAdmin(admin.ModelAdmin):
    list_display = (
        "item",
        "quantity",
        "reason",
        "business_date",
        "recorded_by",
        "location",
    )
    list_filter = ("location", "reason", "business_date")
    search_fields = ("item__name",)
    date_hierarchy = "business_date"
    readonly_fields = ("recorded_at",)
    autocomplete_fields = ("item",)