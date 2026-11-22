from rest_framework import serializers

from cart.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.CharField(source="product.price", read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "product_price", "quantity", "created_at"]
        read_only_fields = ["id", "created_at"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["user", "created_at", "items", "item_count", "total_amount"]
        read_only_fields = ["user", "created_at"]

    def get_item_count(self, obj):
        return obj.items.count()

    def get_total_amount(self, obj):
        return sum((item.product.price * item.quantity) for item in obj.items.all())
