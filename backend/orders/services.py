"""Business logic for order lifecycle transitions."""

from orders.models import Order, TransactionStatus


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
        raise ValueError(
            f"Cannot transition from {current} to {new_status_code}"
        )
    order.status_code = TransactionStatus.objects.get(code=new_status_code)
    order.save()
    return order
