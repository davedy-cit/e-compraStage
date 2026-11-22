from django.db import models
from django.utils import timezone


# Create your models here.
class DeliveryBooking(models.Model):
    id = models.BigAutoField(primary_key=True)
    transaction = models.OneToOneField("Transaction", models.CASCADE, related_name="delivery_booking")
    provider = models.CharField(max_length=24)
    booking_reference = models.CharField(max_length=120)
    tracking_url = models.CharField(max_length=500)
    fee = models.DecimalField(max_digits=12, decimal_places=2)
    status_code = models.ForeignKey("DeliveryStatus", models.DO_NOTHING, db_column="status_code")
    raw_response = models.JSONField(blank=True, null=True)
    booked_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "orders_deliverybooking"


class DeliveryStatus(models.Model):
    code = models.CharField(primary_key=True, max_length=16)
    description = models.CharField(max_length=120)
    is_terminal = models.IntegerField()

    class Meta:
        managed = False
        db_table = "orders_deliverystatus"


class FulfillmentMethod(models.Model):
    code = models.CharField(primary_key=True, max_length=16)
    description = models.CharField(max_length=120)

    class Meta:
        managed = False
        db_table = "orders_fulfillmentmethod"


class Order(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey("accounts.AuthUser", models.SET_NULL, blank=True, null=True)
    customer_label = models.CharField(max_length=120, blank=True, null=True)
    vendor = models.ForeignKey("catalog.Vendor", models.DO_NOTHING)
    status_code = models.ForeignKey("TransactionStatus", models.DO_NOTHING, db_column="status_code")
    fulfillment_code = models.ForeignKey("FulfillmentMethod", models.DO_NOTHING, db_column="fulfillment_code")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "orders_order"


class OrderItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey("Order", models.CASCADE, related_name="items")
    product = models.ForeignKey("catalog.Product", models.DO_NOTHING)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "orders_orderitem"
        unique_together = (("order", "product"),)


class Payment(models.Model):
    id = models.BigAutoField(primary_key=True)
    transaction = models.ForeignKey("Transaction", models.CASCADE, related_name="payments")
    provider = models.CharField(max_length=24)
    provider_reference = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status_code = models.ForeignKey("PaymentStatus", models.DO_NOTHING, db_column="status_code")
    raw_response = models.JSONField(blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "orders_payment"
        unique_together = (("provider", "provider_reference"),)


class PaymentStatus(models.Model):
    code = models.CharField(primary_key=True, max_length=16)
    description = models.CharField(max_length=120)
    is_terminal = models.IntegerField()

    class Meta:
        managed = False
        db_table = "orders_paymentstatus"


class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.OneToOneField(Order, models.CASCADE, related_name="transaction")
    transaction_type = models.ForeignKey("TransactionType", models.DO_NOTHING, db_column="transaction_type")
    reference_no = models.CharField(unique=True, max_length=40)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        managed = False
        db_table = "orders_transaction"


class TransactionStatus(models.Model):
    code = models.CharField(primary_key=True, max_length=24)
    description = models.CharField(max_length=120)
    sort_order = models.IntegerField()

    class Meta:
        managed = False
        db_table = "orders_transactionstatus"


class TransactionType(models.Model):
    code = models.CharField(primary_key=True, max_length=24)
    description = models.CharField(max_length=120)

    class Meta:
        managed = False
        db_table = "orders_transactiontype"

    def __str__(self):
        return self.name
