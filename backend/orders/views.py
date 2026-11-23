from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    DeliveryStatus,
    FulfillmentMethod,
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
from .services import checkout_cart


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
        fulfillment_code = request.data.get("fulfillment_code", "DELIVERY")
        try:
            order_ids = checkout_cart(request.user, fulfillment_code=fulfillment_code)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"order_ids": order_ids, "status": "checkout_complete"},
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
            return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

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
