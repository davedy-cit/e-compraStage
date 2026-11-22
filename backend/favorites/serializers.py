from catalog.serializers import ProductSerializer, VendorSerializer
from rest_framework import serializers

from .models import FavoriteProduct, FavoriteVendor


class FavoriteProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = FavoriteProduct
        fields = ("id", "product", "created_at")


class FavoriteVendorSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True)

    class Meta:
        model = FavoriteVendor
        fields = ("id", "vendor", "created_at")
