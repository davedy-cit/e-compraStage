from rest_framework import serializers

from .models import AvailabilityStatus, Category, Product, UnitOfMeasure, Vendor


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug")


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ("id", "name", "stall_location", "market_section", "contact_phone", "contact_email")


class ProductSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    unit = serializers.CharField(source="unit_code.code", read_only=True)
    availability = serializers.CharField(source="availability_code.code", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "description",
            "image_url",
            "vendor",
            "category",
            "unit",
            "price",
            "stock_quantity",
            "low_stock_threshold",
            "availability",
            "stall_location",
            "comparison_group",
        )


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = ("code", "name", "description")


class AvailabilityStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilityStatus
        fields = ("code", "description", "is_orderable")
