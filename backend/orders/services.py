"""Business logic for order lifecycle transitions."""

from cart.models import Cart, CartItem

from orders.models import (
    FulfillmentMethod,
    Order,
    OrderItem,
    Transaction,
    TransactionStatus,
    TransactionType,
)

ALLOWED_TRANSITIONS = {
    "PENDING_PAYMENT": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["PREPARING", "CANCELLED"],
    "PREPARING": ["OUT_FOR_DELIVERY", "CANCELLED"],
    "OUT_FOR_DELIVERY": ["COMPLETED", "CANCELLED"],
    "COMPLETED": [],
    "CANCELLED": [],
}


def transition_order_status(order, new_status_code):
    """Validate and apply an order status transition."""
    current = order.status_code.code
    allowed = ALLOWED_TRANSITIONS.get(current, [])
    if new_status_code not in allowed:
        raise ValueError(f"Cannot transition from {current} to {new_status_code}")
    order.status_code = TransactionStatus.objects.get(code=new_status_code)
    order.save()
    return order


def checkout_cart(user, fulfillment_code="DELIVERY"):
    """Split cart by vendor and create orders + transactions."""
    cart, _ = Cart.objects.get_or_create(user=user)
    items = CartItem.objects.filter(cart=cart).select_related("product", "product__vendor")

    if not items.exists():
        raise ValueError("Cart is empty")

    by_vendor = {}
    for item in items:
        by_vendor.setdefault(item.product.vendor_id, []).append(item)

    order_ids = []
    transaction_ids = []
    for vendor_id, vendor_items in by_vendor.items():
        total = sum((item.product.price * item.quantity) for item in vendor_items)
        order = Order.objects.create(
            user=user,
            vendor_id=vendor_id,
            status_code=TransactionStatus.objects.get(code="PENDING_PAYMENT"),
            fulfillment_code=FulfillmentMethod.objects.get(code=fulfillment_code),
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
        transaction = Transaction.objects.create(
            order=order,
            transaction_type=TransactionType.objects.get(code="ONLINE_ORDER"),
            reference_no=f"TXN-{order.id}-{vendor_id}",
        )
        order_ids.append(order.id)
        transaction_ids.append(transaction.id)

    CartItem.objects.filter(cart=cart).delete()
    return order_ids, transaction_ids
