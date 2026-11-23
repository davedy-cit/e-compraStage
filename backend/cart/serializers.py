from rest_framework import serializers

from cart.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.CharField(source="product.price", read_only=True)
    vendor_id = serializers.IntegerField(source="product.vendor.id", read_only=True)
    vendor_name = serializers.CharField(source="product.vendor.name", read_only=True)
    stall_location = serializers.CharField(source="product.vendor.stall_location", read_only=True)
    section_name = serializers.CharField(source="product.vendor.section_name", read_only=True)
    category_name = serializers.CharField(source="product.category.name", read_only=True)
    unit = serializers.CharField(source="product.unit_code.code", read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id", "product", "product_name", "product_price", "quantity", "created_at",
            "vendor_id", "vendor_name", "stall_location", "section_name",
            "category_name", "unit"
        ]
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
