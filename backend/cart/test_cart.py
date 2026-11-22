import pytest
from cart.models import Cart, CartItem


@pytest.mark.django_db
def test_cart_add_item(api_client, user, product):
    api_client.force_authenticate(user=user)
    resp = api_client.post("/api/cart/add/", {"product_id": product.id, "quantity": 2})
    assert resp.status_code == 200
    assert CartItem.objects.filter(cart__user=user).count() == 1
    assert resp.data["items"][0]["quantity"] == 2


@pytest.mark.django_db
def test_cart_add_item_increments_quantity(api_client, user, product):
    """Adding same product twice should increment quantity."""
    api_client.force_authenticate(user=user)
    api_client.post("/api/cart/add/", {"product_id": product.id, "quantity": 2})
    resp = api_client.post("/api/cart/add/", {"product_id": product.id, "quantity": 3})
    assert resp.status_code == 200
    assert CartItem.objects.filter(cart__user=user).count() == 1
    assert resp.data["items"][0]["quantity"] == 5


@pytest.mark.django_db
def test_cart_insufficient_stock(api_client, user, low_stock_product):
    api_client.force_authenticate(user=user)
    resp = api_client.post("/api/cart/add/", {"product_id": low_stock_product.id, "quantity": 999})
    assert resp.status_code == 400
    assert "error" in resp.data or "Insufficient stock" in str(resp.data)


@pytest.mark.django_db
def test_cart_update_item_quantity(api_client, user, product):
    api_client.force_authenticate(user=user)
    # Add item first
    api_client.post("/api/cart/add/", {"product_id": product.id, "quantity": 2})
    # Get the cart to find item_id
    cart_resp = api_client.get("/api/cart/")
    item_id = cart_resp.data["items"][0]["id"]
    # Update quantity
    resp = api_client.post("/api/cart/update_item/", {"item_id": item_id, "quantity": 5})
    assert resp.status_code == 200
    assert resp.data["items"][0]["quantity"] == 5


@pytest.mark.django_db
def test_cart_update_item_to_zero_removes(api_client, user, product):
    """Setting quantity to 0 should remove the item."""
    api_client.force_authenticate(user=user)
    api_client.post("/api/cart/add/", {"product_id": product.id, "quantity": 2})
    cart_resp = api_client.get("/api/cart/")
    item_id = cart_resp.data["items"][0]["id"]
    resp = api_client.post("/api/cart/update_item/", {"item_id": item_id, "quantity": 0})
    assert resp.status_code == 200
    assert len(resp.data["items"]) == 0


@pytest.mark.django_db
def test_cart_remove_item(api_client, user, product):
    api_client.force_authenticate(user=user)
    api_client.post("/api/cart/add/", {"product_id": product.id, "quantity": 2})
    cart_resp = api_client.get("/api/cart/")
    item_id = cart_resp.data["items"][0]["id"]
    resp = api_client.post("/api/cart/remove_item/", {"item_id": item_id})
    assert resp.status_code == 200
    assert len(resp.data["items"]) == 0


@pytest.mark.django_db
def test_cart_view_empty(api_client, user):
    api_client.force_authenticate(user=user)
    resp = api_client.get("/api/cart/")
    assert resp.status_code == 200
    assert resp.data["items"] == []
    assert resp.data["item_count"] == 0
    assert str(resp.data["total_amount"]) in ("0.00", "0", 0)