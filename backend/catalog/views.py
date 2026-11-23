from django.db.models import Q
from rest_framework import generics

from .models import AvailabilityStatus, Category, Product, UnitOfMeasure, Vendor
from .serializers import (
    AvailabilityStatusSerializer,
    CategorySerializer,
    ProductSerializer,
    UnitOfMeasureSerializer,
    VendorSerializer,
)


class ProductList(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.filter(availability_code__is_orderable=True).select_related(
            "vendor", "category", "unit_code", "availability_code"
        )
        q = self.request.query_params.get("q")
        cat = self.request.query_params.get("category")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(vendor__name__icontains=q))
        if cat:
            qs = qs.filter(category__slug=cat)
        return qs.order_by("name")


class ProductFeatured(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(
            availability_code__is_orderable=True
        ).select_related("vendor", "category", "unit_code", "availability_code").order_by("-created_at")[:10]


class ProductDetail(generics.RetrieveAPIView):
    queryset = Product.objects.select_related("vendor", "category", "unit_code", "availability_code")
    serializer_class = ProductSerializer


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer


class VendorList(generics.ListAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


class VendorFeatured(generics.ListAPIView):
    serializer_class = VendorSerializer

    def get_queryset(self):
        return Vendor.objects.all().order_by("?")[:5]


class UnitOfMeasureList(generics.ListAPIView):
    queryset = UnitOfMeasure.objects.filter(is_active=True)
    serializer_class = UnitOfMeasureSerializer


class AvailabilityStatusList(generics.ListAPIView):
    queryset = AvailabilityStatus.objects.filter(is_orderable=True)
    serializer_class = AvailabilityStatusSerializer
