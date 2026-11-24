from accounts.models import AuthUser, Userprofile
from catalog.models import Vendor
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from vendors.models import PosVendor


class PosVendorSerializer(serializers.ModelSerializer):
    """Serializer for POS vendor list."""
    catalog_vendor_name = serializers.CharField(source='catalog_vendor.name', read_only=True)

    class Meta:
        model = PosVendor
        fields = ['id', 'catalog_vendor', 'catalog_vendor_name', 'stall_name', 'stall_location']


class VendorCreateSerializer(serializers.Serializer):
    """Serializer for Market Admin to create vendor accounts."""
    # User account fields
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)

    # Vendor business fields
    name = serializers.CharField(max_length=150, help_text="Business/Stall name")
    stall_location = serializers.CharField(max_length=120)
    market_section = serializers.CharField(max_length=120)
    contact_phone = serializers.CharField(max_length=32)
    contact_email = serializers.EmailField()

    def validate_username(self, value):
        if AuthUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if AuthUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def validate_contact_email(self, value):
        if Vendor.objects.filter(contact_email__iexact=value).exists():
            raise serializers.ValidationError("Vendor contact email already in use")
        return value

    @transaction.atomic
    def create(self, validated_data):
        # Extract user fields
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'password': validated_data.pop('password'),
        }
        vendor_data = validated_data

        # Create AuthUser
        user = AuthUser.objects.create(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password=make_password(user_data['password']),
            is_active=1,
            is_staff=0,  # Not admin
            is_superuser=0,
            date_joined=timezone.now(),
        )

        # Create Userprofile (is_vendor=1)
        Userprofile.objects.create(
            user=user,
            is_vendor=1,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # Create Catalog Vendor (links to user)
        vendor = Vendor.objects.create(
            name=vendor_data['name'],
            stall_location=vendor_data['stall_location'],
            market_section=vendor_data['market_section'],
            contact_phone=vendor_data['contact_phone'],
            contact_email=vendor_data['contact_email'],
            is_active=1,
            user=user,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # Create PosVendor (links to catalog Vendor)
        PosVendor.objects.create(
            catalog_vendor=vendor,
            stall_name=vendor_data['name'],
            stall_location=vendor_data['stall_location'],
        )

        return vendor


class VendorListSerializer(serializers.ModelSerializer):
    """Serializer for admin vendor list view."""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_is_active = serializers.IntegerField(source='user.is_active', read_only=True)

    class Meta:
        model = Vendor
        fields = [
            'id', 'name', 'stall_location', 'market_section',
            'contact_phone', 'contact_email', 'is_active',
            'user_email', 'user_username', 'user_is_active',
            'created_at', 'updated_at',
        ]


class VendorDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single vendor."""
    user = serializers.SerializerMethodField()
    pos_vendor = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = '__all__'

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'is_active': obj.user.is_active,
            'date_joined': obj.user.date_joined,
        }

    def get_pos_vendor(self, obj):
        try:
            pv = obj.posvendor  # reverse OneToOne
            return {
                'id': pv.catalog_vendor_id,
                'stall_name': pv.stall_name,
                'stall_location': pv.stall_location,
            }
        except PosVendor.DoesNotExist:
            return None
