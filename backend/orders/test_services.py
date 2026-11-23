"""Tests for orders services layer."""

import pytest

from orders.models import TransactionStatus
from orders.services import checkout_cart, transition_order_status


@pytest.mark.django_db
def test_transition_order_status_valid(user, vendor, product):
    """Test valid order status transitions."""
    from orders.models import FulfillmentMethod, Order, Transaction, TransactionType
    order = Order.objects.create(
        user=user, vendor=vendor,
        status_code=TransactionStatus.objects.get(code="PENDING_PAYMENT"),
        fulfillment_code=FulfillmentMethod.objects.get(code="DELIVERY"),
        total_amount=100, notes=""
    )
    Transaction.objects.create(order=order, transaction_type=TransactionType.objects.get(code="ONLINE_ORDER"), reference_no=f"TXN-{order.id}")

    order = transition_order_status(order, "CONFIRMED")
    assert order.status_code.code == "CONFIRMED"

    order = transition_order_status(order, "PREPARING")
    assert order.status_code.code == "PREPARING"


@pytest.mark.django_db
def test_transition_order_status_invalid(user, vendor, product):
    """Test invalid order status transitions raise ValueError."""
    from orders.models import FulfillmentMethod, Order, Transaction, TransactionType
    order = Order.objects.create(
        user=user, vendor=vendor,
        status_code=TransactionStatus.objects.get(code="PENDING_PAYMENT"),
        fulfillment_code=FulfillmentMethod.objects.get(code="DELIVERY"),
        total_amount=100, notes=""
    )
    Transaction.objects.create(order=order, transaction_type=TransactionType.objects.get(code="ONLINE_ORDER"), reference_no=f"TXN-{order.id}")

    with pytest.raises(ValueError):
        transition_order_status(order, "OUT_FOR_DELIVERY")  # Skip CONFIRMED, PREPARING


@pytest.mark.django_db
def test_transition_order_status_terminal(user, vendor, product):
    """Test transitions from terminal states (COMPLETED, CANCELLED) fail."""
    from orders.models import FulfillmentMethod, Order, Transaction, TransactionType
    order = Order.objects.create(
        user=user, vendor=vendor,
        status_code=TransactionStatus.objects.get(code="COMPLETED"),
        fulfillment_code=FulfillmentMethod.objects.get(code="DELIVERY"),
        total_amount=100, notes=""
    )
    Transaction.objects.create(order=order, transaction_type=TransactionType.objects.get(code="ONLINE_ORDER"), reference_no=f"TXN-{order.id}")

    with pytest.raises(ValueError):
        transition_order_status(order, "CANCELLED")


@pytest.mark.django_db
def test_checkout_cart_splits_by_vendor(user, multi_vendor_cart):
    """Test checkout splits cart items by vendor into separate orders."""
    order_ids, _ = checkout_cart(user)
    assert len(order_ids) == len(multi_vendor_cart)
    # Verify each order belongs to a different vendor
    vendor_ids = set()
    for oid in order_ids:
        from orders.models import Order
        vendor_ids.add(Order.objects.get(id=oid).vendor_id)
    assert len(vendor_ids) == len(multi_vendor_cart)


@pytest.mark.django_db
def test_checkout_cart_returns_order_and_transaction_ids(user, multi_vendor_cart):
    """Test checkout returns both order_ids and transaction_ids."""
    from orders.services import checkout_cart
    order_ids, transaction_ids = checkout_cart(user)
    assert len(order_ids) == len(multi_vendor_cart)
    assert len(transaction_ids) == len(multi_vendor_cart)
    # Verify each order has a corresponding transaction
    from orders.models import Transaction
    for order_id, transaction_id in zip(order_ids, transaction_ids, strict=True):
        txn = Transaction.objects.get(id=transaction_id)
        assert txn.order_id == order_id


@pytest.mark.django_db
def test_checkout_cart_empty_cart_raises_error(user):
    """Test checkout with empty cart raises ValueError."""
    with pytest.raises(ValueError, match="Cart is empty"):
        checkout_cart(user)
