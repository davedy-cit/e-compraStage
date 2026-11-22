from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, CartItem

from .models import (
    DeliveryStatus,
    FulfillmentMethod,
    Order,
    OrderItem,
    Payment,
    PaymentStatus,
    Transaction,
    TransactionStatus,
    TransactionType,
)
from .serializers import (
    DeliveryStatusSerializer,
    FulfillmentMethodSerializer,
    PaymentStatusSerializer,
    TransactionStatusSerializer,
    TransactionTypeSerializer,
)


class TransactionStatusList(generics.ListAPIView):
    queryset = TransactionStatus.objects.all()
    serializer_class = TransactionStatusSerializer


class TransactionTypeList(generics.ListAPIView):
    queryset = TransactionType.objects.all()
    serializer_class = TransactionTypeSerializer


class PaymentStatusList(generics.ListAPIView):
    queryset = PaymentStatus.objects.all()
    serializer_class = PaymentStatusSerializer


class DeliveryStatusList(generics.ListAPIView):
    queryset = DeliveryStatus.objects.all()
    serializer_class = DeliveryStatusSerializer


class FulfillmentMethodList(generics.ListAPIView):
    queryset = FulfillmentMethod.objects.all()
    serializer_class = FulfillmentMethodSerializer


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cart, _ = Cart.objects.get_or_create(user=user)
        items = (
            CartItem.objects.filter(cart=cart)
            .select_related("product", "product__vendor")
        )

        if not items.exists():
            return Response(
                {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Split by vendor
        by_vendor = {}
        for item in items:
            by_vendor.setdefault(item.product.vendor_id, []).append(item)

        orders = []
        pending_status = TransactionStatus.objects.get(code="PENDING_PAYMENT")
        delivery_method = FulfillmentMethod.objects.get(code="DELIVERY")
        online_order_type = TransactionType.objects.get(code="ONLINE_ORDER")

        for vendor_id, vendor_items in by_vendor.items():
            total = sum(
                (item.product.price * item.quantity) for item in vendor_items
            )
            order = Order.objects.create(
                user=user,
                vendor_id=vendor_id,
                status_code=pending_status,
                fulfillment_code=delivery_method,
                total_amount=total,
                notes="",
            )
            for item in vendor_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.price,
                )
            Transaction.objects.create(
                order=order,
                transaction_type=online_order_type,
                reference_no=f"TXN-{order.id}-{vendor_id}",
            )
            orders.append(order.id)

        # Clear cart
        CartItem.objects.filter(cart=cart).delete()

        return Response(
            {"order_ids": orders, "status": "checkout_complete"},
            status=status.HTTP_201_CREATED,
        )


class PaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        transaction_id = request.data.get("transaction_id")
        provider = request.data.get("provider")
        provider_reference = request.data.get("provider_reference")
        amount = request.data.get("amount")

        try:
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return Response(
                {"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND
            )

        verified_status = PaymentStatus.objects.get(code="VERIFIED")
        payment = Payment.objects.create(
            transaction=transaction,
            provider=provider,
            provider_reference=provider_reference,
            amount=amount,
            status_code=verified_status,
        )

        return Response(
            {
                "payment_id": payment.id,
                "status": payment.status_code.code,
                "amount": str(payment.amount),
            },
            status=status.HTTP_201_CREATED,
        )
