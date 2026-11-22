import pytest
from datetime import datetime
from django.contrib.auth.hashers import make_password
from accounts.models import AuthUser
from catalog.models import Product, Vendor, Category, UnitOfMeasure, AvailabilityStatus
from cart.models import Cart, CartItem


def _create_auth_user(username, email, password="testpass", **kwargs):
    """Create an AuthUser with DRF-compatible is_authenticated property."""
    user = AuthUser.objects.create(
        username=username,
        password=make_password(password),
        email=email,
        first_name=kwargs.get("first_name", ""),
        last_name=kwargs.get("last_name", ""),
        is_staff=kwargs.get("is_staff", 0),
        is_active=kwargs.get("is_active", 1),
        is_superuser=kwargs.get("is_superuser", 0),
        date_joined=datetime.now(),
        last_login=datetime.now(),
    )
    # Add DRF-required property
    user.is_authenticated = True
    return user


@pytest.fixture
def user():
    return _create_auth_user("testuser", "test@test.com")


@pytest.fixture
def vendor_user():
    return _create_auth_user("vendoruser", "vendor@test.com", first_name="Vendor", last_name="User")


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def category():
    now = datetime.now()
    return Category.objects.create(
        name="Produce", slug="produce", is_active=1,
        created_at=now, updated_at=now
    )


@pytest.fixture
def unit():
    now = datetime.now()
    return UnitOfMeasure.objects.create(
        code="PCS", name="Piece", description="Per piece", is_active=1,
        created_at=now, updated_at=now
    )


@pytest.fixture
def availability():
    # AvailabilityStatus does NOT have created_at/updated_at - use get_or_create
    return AvailabilityStatus.objects.get_or_create(
        code="IN_STOCK",
        defaults={"description": "In stock", "sort_order": 1, "is_orderable": 1}
    )[0]


@pytest.fixture
def vendor(vendor_user):
    now = datetime.now()
    return Vendor.objects.create(
        name="Test Vendor",
        stall_location="A1",
        market_section="Main",
        contact_phone="1234567890",
        contact_email="vendor@test.com",
        is_active=1,
        user=vendor_user,
        created_at=now, updated_at=now
    )


@pytest.fixture
def second_vendor():
    user = _create_auth_user("vendor2", "vendor2@test.com", first_name="Vendor", last_name="Two")
    now = datetime.now()
    return Vendor.objects.create(
        name="Second Vendor",
        stall_location="B2",
        market_section="Main",
        contact_phone="0987654321",
        contact_email="vendor2@test.com",
        is_active=1,
        user=user,
        created_at=now, updated_at=now
    )


@pytest.fixture
def product(category, unit, availability, vendor):
    now = datetime.now()
    return Product.objects.create(
        name="Test Product",
        description="Test product description",
        image_url="",
        vendor=vendor,
        category=category,
        unit_code=unit,
        availability_code=availability,
        price="10.00",
        stock_quantity=100,
        low_stock_threshold=5,
        stall_location="A1",
        comparison_group=None,
        created_at=now, updated_at=now
    )


@pytest.fixture
def low_stock_product(category, unit, availability, vendor):
    now = datetime.now()
    return Product.objects.create(
        name="Low Stock Product",
        description="Low stock product",
        image_url="",
        vendor=vendor,
        category=category,
        unit_code=unit,
        availability_code=availability,
        price="20.00",
        stock_quantity=2,
        low_stock_threshold=5,
        stall_location="A1",
        comparison_group=None,
        created_at=now, updated_at=now
    )


@pytest.fixture
def second_vendor_product(category, unit, availability, second_vendor):
    now = datetime.now()
    return Product.objects.create(
        name="Second Vendor Product",
        description="Product from second vendor",
        image_url="",
        vendor=second_vendor,
        category=category,
        unit_code=unit,
        availability_code=availability,
        price="15.00",
        stock_quantity=50,
        low_stock_threshold=5,
        stall_location="B2",
        comparison_group=None,
        created_at=now, updated_at=now
    )


@pytest.fixture
def multi_vendor_cart(user, product, second_vendor_product):
    """Create a cart with items from multiple vendors."""
    now = datetime.now()
    # Delete any existing cart for this user
    Cart.objects.filter(user=user).delete()
    cart = Cart.objects.create(user=user, created_at=now)
    CartItem.objects.create(cart=cart, product=product, quantity=2, created_at=now)
    CartItem.objects.create(cart=cart, product=second_vendor_product, quantity=1, created_at=now)
    return [product.vendor_id, second_vendor_product.vendor_id]


@pytest.fixture
def transaction_status_pending():
    from orders.models import TransactionStatus
    # TransactionStatus does NOT have created_at/updated_at
    return TransactionStatus.objects.get_or_create(
        code="PENDING_PAYMENT",
        defaults={"description": "Pending Payment", "sort_order": 1}
    )[0]


@pytest.fixture
def fulfillment_method_delivery():
    from orders.models import FulfillmentMethod
    # FulfillmentMethod does NOT have created_at/updated_at
    return FulfillmentMethod.objects.get_or_create(
        code="DELIVERY",
        defaults={"description": "Delivery"}
    )[0]


@pytest.fixture
def transaction_type_online():
    from orders.models import TransactionType
    # TransactionType does NOT have created_at/updated_at
    return TransactionType.objects.get_or_create(
        code="ONLINE_ORDER",
        defaults={"description": "Online Order"}
    )[0]


@pytest.fixture
def payment_status_verified():
    from orders.models import PaymentStatus
    # PaymentStatus does NOT have created_at/updated_at
    return PaymentStatus.objects.get_or_create(
        code="VERIFIED",
        defaults={"description": "Verified", "is_terminal": 1}
    )[0]