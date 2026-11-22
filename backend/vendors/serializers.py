from rest_framework import serializers

from .models import PosVendor, VendorTransaction


class PosVendorSerializer(serializers.ModelSerializer):
    catalog_vendor_name = serializers.CharField(source="catalog_vendor.name", read_only=True)

    class Meta:
        model = PosVendor
        fields = ("catalog_vendor", "catalog_vendor_name", "stall_name", "stall_location")


class VendorTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorTransaction
        fields = ("id", "vendor", "order", "status", "receipt_serial", "receipt_attempt", "created_at")
