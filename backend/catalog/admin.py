from django.contrib import admin

from .models import (
    AvailabilityStatus,
    Category,
    ComparisonGroup,
    ComparisonGroupUnit,
    InventoryMovement,
    InventoryReason,
    Product,
    UnitOfMeasure,
    Vendor,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "vendor",
        "category",
        "price",
        "unit_code",
        "stock_quantity",
        "availability_code",
        "low_stock_threshold",
    )
    list_filter = ("category", "availability_code", "vendor")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "stall_location",
        "market_section",
        "contact_phone",
        "contact_email",
        "is_active",
        "user",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "stall_location", "contact_email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at", "updated_at")
    prepopulated_fields = {}
    search_fields = ("name",)


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    search_fields = ("code", "name")


@admin.register(ComparisonGroup)
class ComparisonGroupAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "base_unit", "is_active")
    search_fields = ("code", "name")


admin.site.register(ComparisonGroupUnit)
admin.site.register(AvailabilityStatus)
admin.site.register(InventoryReason)
admin.site.register(InventoryMovement)
