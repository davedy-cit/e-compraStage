"""Business logic for cart operations."""

from catalog.models import Product

from cart.models import Cart, CartItem


def add_to_cart(user, product_id, quantity):
    product = Product.objects.get(id=product_id)
    if product.stock_quantity < quantity:
        raise ValueError("Insufficient stock")
    cart, _ = Cart.objects.get_or_create(user=user)
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, defaults={"quantity": quantity}
    )
    if not created:
        if product.stock_quantity < item.quantity + quantity:
            raise ValueError("Insufficient stock")
        item.quantity += quantity
        item.save()
    return cart


def update_cart_item(user, item_id, quantity):
    cart, _ = Cart.objects.get_or_create(user=user)
    item = CartItem.objects.get(id=item_id, cart=cart)
    if quantity <= 0:
        item.delete()
    else:
        if item.product.stock_quantity < quantity:
            raise ValueError("Insufficient stock")
        item.quantity = quantity
        item.save()
    return cart


def remove_cart_item(user, item_id):
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.filter(id=item_id, cart=cart).delete()
    return cart
