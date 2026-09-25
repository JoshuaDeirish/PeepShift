from django.contrib import admin
from .models import (
    Station,
    ChecklistTemplate,
    TemplateVersion,
    TemplateItem,
    ChecklistRun,
    ItemCompletion,
)


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "is_active")
    list_filter = ("location", "is_active")
    search_fields = ("name",)


@admin.register(ChecklistTemplate)
class ChecklistTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "is_active", "created_at")
    list_filter = ("location", "is_active")
    search_fields = ("name",)


class TemplateItemInline(admin.TabularInline):
    model = TemplateItem
    extra = 1
    fields = ("station", "order", "text")
    ordering = ("station", "order")


@admin.register(TemplateVersion)
class TemplateVersionAdmin(admin.ModelAdmin):
    list_display = ("template", "version_number", "published_at", "published_by")
    list_filter = ("template", "published_at")
    inlines = [TemplateItemInline]
    readonly_fields = ("created_at",)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_published:
            return ("template", "version_number", "published_at", "published_by", "created_at")
        return self.readonly_fields

    def has_change_permission(self, request, obj=None):
        if obj and obj.is_published:
            return False
        return super().has_change_permission(request, obj)


class ItemCompletionInline(admin.TabularInline):
    model = ItemCompletion
    extra = 0
    fields = ("item", "completed_by", "completed_at", "note")
    readonly_fields = ("completed_at",)


@admin.register(ChecklistRun)
class ChecklistRunAdmin(admin.ModelAdmin):
    list_display = ("station", "business_date", "version", "signed_off_at", "signed_off_by")
    list_filter = ("station", "business_date", "signed_off_at")
    date_hierarchy = "business_date"
    inlines = [ItemCompletionInline]


@admin.register(ItemCompletion)
class ItemCompletionAdmin(admin.ModelAdmin):
    list_display = ("item", "run", "completed_by", "completed_at")
    list_filter = ("completed_by", "completed_at")
    readonly_fields = ("completed_at",)