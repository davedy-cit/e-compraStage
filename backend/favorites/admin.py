from django.contrib import admin
from .models import FavoriteProduct, FavoriteVendor

@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")

@admin.register(FavoriteVendor)
class FavoriteVendorAdmin(admin.ModelAdmin):
    list_display = ("user", "vendor", "created_at")
    search_fields = ("user__username", "vendor__name")