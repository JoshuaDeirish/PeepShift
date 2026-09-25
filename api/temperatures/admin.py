from django.contrib import admin
from .models import Equipment, TemperatureReading


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "min_temp", "max_temp", "location", "is_active")
    list_filter = ("location", "type", "is_active")
    search_fields = ("name",)
    list_editable = ("is_active",)


@admin.register(TemperatureReading)
class TemperatureReadingAdmin(admin.ModelAdmin):
    list_display = (
        "equipment",
        "temperature",
        "out_of_range",
        "business_date",
        "recorded_by",
    )
    list_filter = ("location", "equipment", "business_date")
    date_hierarchy = "business_date"
    readonly_fields = ("recorded_at",)
    autocomplete_fields = ("equipment",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("equipment", "recorded_by")

    @admin.display(boolean=True, description="Out of range")
    def out_of_range(self, obj):
        return obj.is_out_of_range