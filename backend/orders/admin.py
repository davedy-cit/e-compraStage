from django.contrib import admin

from .models import (
    DeliveryBooking,
    DeliveryStatus,
    FulfillmentMethod,
    Order,
    OrderItem,
    Payment,
    PaymentStatus,
    Transaction,
    TransactionStatus,
    TransactionType,
)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "customer_label",
        "vendor",
        "status_code",
        "fulfillment_code",
        "total_amount",
        "created_at",
    )
    list_filter = ("status_code", "fulfillment_code", "vendor")
    search_fields = ("id", "user__username", "customer_label", "vendor__name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "unit_price")
    search_fields = ("order__id", "product__name")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "transaction_type", "reference_no", "created_at")
    search_fields = ("reference_no", "order__id")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "transaction", "provider", "amount", "status_code", "paid_at")
    list_filter = ("status_code", "provider")
    search_fields = ("provider_reference",)


@admin.register(DeliveryBooking)
class DeliveryBookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "transaction",
        "provider",
        "booking_reference",
        "status_code",
        "fee",
        "delivered_at",
    )
    list_filter = ("status_code", "provider")
    search_fields = ("booking_reference",)


admin.site.register(TransactionStatus)
admin.site.register(TransactionType)
admin.site.register(PaymentStatus)
admin.site.register(DeliveryStatus)
admin.site.register(FulfillmentMethod)
