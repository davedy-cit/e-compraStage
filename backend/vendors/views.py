from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order, TransactionStatus
from orders.serializers import OrderSerializer

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
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        order.status_code = TransactionStatus.objects.get(code=new_status_code)
        order.save()
        return Response(OrderSerializer(order, context={"request": request}).data)
