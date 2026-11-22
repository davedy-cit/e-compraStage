from django.db import models


class Cart(models.Model):
    user = models.OneToOneField("accounts.AuthUser", models.CASCADE, primary_key=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "cart_cart"


class CartItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    cart = models.ForeignKey("Cart", models.CASCADE)
    product = models.ForeignKey("catalog.Product", models.CASCADE)
    quantity = models.IntegerField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "cart_cartitem"
        unique_together = (("cart", "product"),)

    def __str__(self):
        return self.product.name
