from rest_framework import serializers

from accounts.models import AuthUser


class CurrentUserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = AuthUser
        fields = ["id", "username", "email", "first_name", "last_name", "role", "profile"]

    def get_role(self, obj):
        if hasattr(obj, "vendor") and obj.vendor:
            return "vendor"
        if hasattr(obj, "customerprofile"):
            return "customer"
        return "customer"

    def get_profile(self, obj):
        if hasattr(obj, "vendor") and obj.vendor:
            return {
                "id": obj.vendor.id,
                "name": obj.vendor.name,
                "stall_location": obj.vendor.stall_location,
            }
        if hasattr(obj, "customerprofile"):
            return {
                "id": obj.customerprofile.id,
                "phone": obj.customerprofile.phone,
                "address": obj.customerprofile.address,
            }
        return None
