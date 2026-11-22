from django.db import models

# Create your models here.

class FavoriteProduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('accounts.AuthUser', models.CASCADE)
    product = models.ForeignKey('catalog.Product', models.CASCADE)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'favorites_favoriteproduct'
        unique_together = (('user', 'product'),)


class FavoriteVendor(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('accounts.AuthUser', models.CASCADE)
    vendor = models.ForeignKey('catalog.Vendor', models.CASCADE)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'favorites_favoritevendor'
        unique_together = (('user', 'vendor'),)

    def __str__(self):
        return self.name

