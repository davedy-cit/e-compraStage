from django.contrib import admin
from .models import PosVendor, VendorTransaction

@admin.register(PosVendor)
class PosVendorAdmin(admin.ModelAdmin):
    list_display = ("catalog_vendor", "stall_name", "stall_location")
    search_fields = ("stall_name", "catalog_vendor__name")

@admin.register(VendorTransaction)
class VendorTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "vendor", "order", "status_code", "receipt_serial", "receipt_attempt", "created_at")
    list_filter = ("status_code",)
    search_fields = ("receipt_serial", "order__id")