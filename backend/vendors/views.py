from orders.models import Order
from orders.serializers import OrderSerializer
from orders.services import transition_order_status
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PosVendor
from .serializers import PosVendorSerializer


class PosVendorList(generics.ListAPIView):
    queryset = PosVendor.objects.select_related("catalog_vendor")
    serializer_class = PosVendorSerializer


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
