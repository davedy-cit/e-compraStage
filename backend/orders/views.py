from rest_framework import generics

from .models import DeliveryStatus, FulfillmentMethod, PaymentStatus, TransactionStatus, TransactionType
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
