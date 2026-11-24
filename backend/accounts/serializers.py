from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from accounts.models import AuthUser, Customerprofile, Userprofile
from rest_framework_simplejwt.tokens import RefreshToken


class CurrentUserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = AuthUser
        fields = ["id", "username", "email", "first_name", "last_name", "role", "profile"]

    def get_role(self, obj):
        # Check is_staff first (Market Admin)
        if obj.is_staff_bool:
            return "admin"
        # Then vendor
        if hasattr(obj, "vendor") and obj.vendor:
            return "vendor"
        # Default customer
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
                "id": obj.customerprofile.user.id,
                "phone": obj.customerprofile.phone,
                "address": obj.customerprofile.address,
            }
        return None


class RegisterSerializer(serializers.ModelSerializer):
    """Customer self-registration serializer."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    phone = serializers.CharField(max_length=32)
    address = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = AuthUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm', 'phone', 'address'
        ]

    def validate_username(self, value):
        if AuthUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if AuthUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match"})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        phone = validated_data.pop('phone')
        address = validated_data.pop('address', '')
        password = validated_data.pop('password')
        validated_data.pop('password_confirm')

        # Create AuthUser
        user = AuthUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=make_password(password),
            is_active=1,
            is_staff=0,
            is_superuser=0,
            date_joined=timezone.now(),
        )

        # Create Customerprofile
        Customerprofile.objects.create(
            user=user,
            phone=phone,
            address=address,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # Create Userprofile (default: not vendor)
        Userprofile.objects.create(
            user=user,
            is_vendor=0,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        return user