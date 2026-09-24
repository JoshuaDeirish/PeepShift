from django.contrib import admin
from .models import Organization, Location


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "timezone", "is_active")
    list_filter = ("is_active", "organization")
    search_fields = ("name", "address")