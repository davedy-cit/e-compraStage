import pytest
from datetime import datetime
from django.contrib.auth.hashers import make_password
from accounts.models import AuthUser
from orders.models import Order, Transaction, Payment
from cart.models import Cart, CartItem


def _create_test_user(username, email):
    """Create a test AuthUser."""
    return AuthUser.objects.create(
        username=username,
        password=make_password("pass"),
        email=email,
        first_name="Test",
        last_name="User",
        is_staff=0,
        is_active=1,
        is_superuser=0,
        date_joined=datetime.now(),
        last_login=datetime.now(),
    )


@pytest.mark.django_db
def test_checkout_splits_by_vendor(api_client, user, multi_vendor_cart):
    api_client.force_authenticate(user=user)
    resp = api_client.post("/api/checkout/")
    assert resp.status_code == 201
    assert "order_ids" in resp.data
    assert len(resp.data["order_ids"]) == len(multi_vendor_cart)
    assert Order.objects.filter(user=user).count() == len(multi_vendor_cart)
    # Each order should have a transaction
    for order_id in resp.data["order_ids"]:
        assert Transaction.objects.filter(order_id=order_id).exists()


@pytest.mark.django_db
def test_checkout_empty_cart_returns_error(api_client, user):
    api_client.force_authenticate(user=user)
    resp = api_client.post("/api/checkout/")
    assert resp.status_code == 400
    assert "error" in resp.data


@pytest.mark.django_db
def test_checkout_clears_cart(api_client, user, product, second_vendor_product):
    api_client.force_authenticate(user=user)
    # Add items to cart
    api_client.post("/api/cart/add/", {"product_id": product.id, "quantity": 2})
    api_client.post("/api/cart/add/", {"product_id": second_vendor_product.id, "quantity": 1})
    # Checkout
    resp = api_client.post("/api/checkout/")
    assert resp.status_code == 201
    # Cart should be empty
    cart_resp = api_client.get("/api/cart/")
    assert cart_resp.data["items"] == []


@pytest.mark.django_db
def test_checkout_creates_correct_order_totals(api_client, user, product, second_vendor_product):
    """Verify order totals match cart item totals."""
    api_client.force_authenticate(user=user)
    api_client.post("/api/cart/add/", {"product_id": product.id, "quantity": 2})  # 2 * 10.00 = 20.00
    api_client.post("/api/cart/add/", {"product_id": second_vendor_product.id, "quantity": 3})  # 3 * 15.00 = 45.00

    resp = api_client.post("/api/checkout/")
    assert resp.status_code == 201

    orders = Order.objects.filter(user=user)
    assert orders.count() == 2

    # Check totals (each vendor gets one order)
    order_totals = {o.vendor_id: o.total_amount for o in orders}
    assert order_totals[product.vendor_id] == 20.00
    assert order_totals[second_vendor_product.vendor_id] == 45.00


@pytest.mark.django_db
def test_payment_records_successfully(api_client, user, product, payment_status_verified, transaction_type_online):
    """Test payment recording for a transaction."""
    api_client.force_authenticate(user=user)
    # First, checkout to create order and transaction
    api_client.post("/api/cart/add/", {"product_id": product.id, "quantity": 1})
    checkout_resp = api_client.post("/api/checkout/")
    assert checkout_resp.status_code == 201

    order_id = checkout_resp.data["order_ids"][0]
    transaction = Transaction.objects.get(order_id=order_id)

    # Record payment
    resp = api_client.post("/api/payment/", {
        "transaction_id": transaction.id,
        "provider": "gcash",
        "provider_reference": "GCASH-12345",
        "amount": str(transaction.order.total_amount),
    })

    assert resp.status_code == 201
    assert resp.data["status"] == "VERIFIED"
    assert Payment.objects.filter(transaction=transaction).exists()


@pytest.mark.django_db
def test_payment_invalid_transaction_returns_404(api_client, user):
    api_client.force_authenticate(user=user)
    resp = api_client.post("/api/payment/", {
        "transaction_id": 99999,
        "provider": "gcash",
        "provider_reference": "GCASH-12345",
        "amount": "10.00",
    })
    assert resp.status_code == 404


@pytest.mark.django_db
def test_vendor_pos_list_orders(api_client, vendor_user, vendor, product):
    """Test vendor can list their orders via POS."""
    from orders.models import Order, TransactionStatus, FulfillmentMethod, TransactionType

    # Create a user and place an order
    customer = _create_test_user("customer", "customer@test.com")

    # Create cart and add item
    from cart.models import Cart, CartItem
    now = datetime.now()
    cart = Cart.objects.create(user=customer, created_at=now)
    CartItem.objects.create(cart=cart, product=product, quantity=1, created_at=now)

    # Create order via checkout (simulate)
    pending_status = TransactionStatus.objects.get(code="PENDING_PAYMENT")
    delivery_method = FulfillmentMethod.objects.get(code="DELIVERY")
    online_type = TransactionType.objects.get(code="ONLINE_ORDER")

    order = Order.objects.create(
        user=customer,
        vendor=vendor,
        status_code=pending_status,
        fulfillment_code=delivery_method,
        total_amount=product.price,
        notes="",
    )
    Transaction.objects.create(
        order=order,
        transaction_type=online_type,
        reference_no=f"TXN-{order.id}-{vendor.id}",
    )

    # Vendor POS list
    api_client.force_authenticate(user=vendor_user)
    resp = api_client.get("/api/vendors/pos/")
    assert resp.status_code == 200
    assert len(resp.data) == 1
    assert resp.data[0]["id"] == order.id


@pytest.mark.django_db
def test_vendor_pos_update_status(api_client, vendor_user, vendor, product):
    """Test vendor can update order status via POS."""
    from orders.models import Order, TransactionStatus, FulfillmentMethod, TransactionType

    customer = _create_test_user("customer2", "customer2@test.com")

    pending_status = TransactionStatus.objects.get(code="PENDING_PAYMENT")
    delivery_method = FulfillmentMethod.objects.get(code="DELIVERY")
    online_type = TransactionType.objects.get(code="ONLINE_ORDER")

    order = Order.objects.create(
        user=customer,
        vendor=vendor,
        status_code=pending_status,
        fulfillment_code=delivery_method,
        total_amount=product.price,
        notes="",
    )
    Transaction.objects.create(
        order=order,
        transaction_type=online_type,
        reference_no=f"TXN-{order.id}-{vendor.id}",
    )

    # Vendor updates status
    api_client.force_authenticate(user=vendor_user)
    resp = api_client.post("/api/vendors/pos/", {
        "order_id": order.id,
        "status_code": "CONFIRMED",
    })

    assert resp.status_code == 200
    assert resp.data["status_code"] == "CONFIRMED"

    order.refresh_from_db()
    assert order.status_code.code == "CONFIRMED"


@pytest.mark.django_db
def test_vendor_pos_invalid_status_transition(api_client, vendor_user, vendor, product):
    """Test invalid status transition is rejected."""
    from orders.models import Order, TransactionStatus, FulfillmentMethod, TransactionType

    customer = _create_test_user("customer3", "customer3@test.com")

    pending_status = TransactionStatus.objects.get(code="PENDING_PAYMENT")
    delivery_method = FulfillmentMethod.objects.get(code="DELIVERY")
    online_type = TransactionType.objects.get(code="ONLINE_ORDER")

    order = Order.objects.create(
        user=customer,
        vendor=vendor,
        status_code=pending_status,
        fulfillment_code=delivery_method,
        total_amount=product.price,
        notes="",
    )
    Transaction.objects.create(
        order=order,
        transaction_type=online_type,
        reference_no=f"TXN-{order.id}-{vendor.id}",
    )

    # Try invalid transition: PENDING_PAYMENT -> OUT_FOR_DELIVERY (skipping CONFIRMED, PREPARING)
    api_client.force_authenticate(user=vendor_user)
    resp = api_client.post("/api/vendors/pos/", {
        "order_id": order.id,
        "status_code": "OUT_FOR_DELIVERY",
    })

    # Should fail - not allowed transition
    assert resp.status_code == 400