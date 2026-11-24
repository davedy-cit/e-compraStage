from accounts.permissions import IsMarketAdmin
from catalog.models import Vendor
from django.db import transaction
from django.utils import timezone
from orders.models import Order
from orders.serializers import OrderSerializer
from orders.services import transition_order_status
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PosVendor
from .serializers import (
    PosVendorSerializer,
    VendorCreateSerializer,
    VendorDetailSerializer,
    VendorListSerializer,
)


class PosVendorList(generics.ListAPIView):
    queryset = PosVendor.objects.select_related("catalog_vendor")
    serializer_class = PosVendorSerializer
    permission_classes = [IsAuthenticated]


class VendorPOSView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(vendor=request.user.vendor)
        serializer = OrderSerializer(orders, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        order_id = request.data.get("order_id")
        new_status_code = request.data.get("status_code")
        try:
            order = Order.objects.get(id=order_id, vendor=request.user.vendor)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            order = transition_order_status(order, new_status_code)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order, context={"request": request}).data)


# === NEW ADMIN ENDPOINTS ===

class AdminVendorListView(generics.ListAPIView):
    """List all vendors for Market Admin."""
    permission_classes = [IsAuthenticated, IsMarketAdmin]
    serializer_class = VendorListSerializer
    queryset = Vendor.objects.select_related('user').all().order_by('-created_at')


class AdminVendorCreateView(APIView):
    """Create vendor account with linked user and profiles."""
    permission_classes = [IsAuthenticated, IsMarketAdmin]

    def post(self, request):
        serializer = VendorCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vendor = serializer.save()

        # Return detailed vendor info
        detail_serializer = VendorDetailSerializer(vendor)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


class AdminVendorDetailView(generics.RetrieveUpdateAPIView):
    """Get or update vendor details."""
    permission_classes = [IsAuthenticated, IsMarketAdmin]
    serializer_class = VendorDetailSerializer
    queryset = Vendor.objects.select_related('user').all()
    lookup_field = 'id'


class AdminVendorDeactivateView(APIView):
    """Soft deactivate vendor (sets is_active=0 on vendor and user)."""
    permission_classes = [IsAuthenticated, IsMarketAdmin]

    @transaction.atomic
    def post(self, request, id):
        try:
            vendor = Vendor.objects.select_related('user').get(id=id)
        except Vendor.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

        vendor.is_active = 0
        vendor.updated_at = timezone.now()
        vendor.save()

        vendor.user.is_active = 0
        vendor.user.save()

        return Response({"message": "Vendor deactivated successfully"})
