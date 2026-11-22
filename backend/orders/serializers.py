from rest_framework import serializers
from .models import (
    Order, OrderItem, Transaction, Payment, DeliveryBooking,
    TransactionStatus, TransactionType, PaymentStatus, DeliveryStatus, FulfillmentMethod
)

class TransactionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionStatus
        fields = ("code", "description")

class TransactionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionType
        fields = ("code", "description")

class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentStatus
        fields = ("code", "description", "is_terminal")

class DeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryStatus
        fields = ("code", "description", "is_terminal")

class FulfillmentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = FulfillmentMethod
        fields = ("code", "description")

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    class Meta:
        model = OrderItem
        fields = ("id", "product", "product_name", "quantity", "unit_price")

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("id", "order", "transaction_type", "reference_no", "created_at")

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "transaction", "provider", "provider_reference", "amount", "status", "paid_at")

class DeliveryBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryBooking
        fields = ("id", "transaction", "provider", "booking_reference", "tracking_url", "fee", "status", "booked_at", "delivered_at")

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    transaction = TransactionSerializer(read_only=True)
    status_display = serializers.CharField(source="status_code.description", read_only=True)
    fulfillment_display = serializers.CharField(source="fulfillment_code.description", read_only=True)

    class Meta:
        model = Order
        fields = ("id", "user", "customer_label", "vendor", "status_code", "status_display",
                  "fulfillment_code", "fulfillment_display", "total_amount", "notes",
                  "created_at", "updated_at", "items", "transaction")