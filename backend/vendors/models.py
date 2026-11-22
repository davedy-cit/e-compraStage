from django.db import models

# Create your models here.
class PosVendor(models.Model):
    catalog_vendor = models.OneToOneField('catalog.Vendor', models.CASCADE, primary_key=True)
    stall_name = models.CharField(max_length=150)
    stall_location = models.CharField(max_length=120)

    class Meta:
        managed = False
        db_table = 'vendors_vendor'


class VendorTransaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    vendor = models.ForeignKey(PosVendor, models.CASCADE)
    order = models.OneToOneField('orders.Order', models.CASCADE)
    status_code = models.ForeignKey('orders.TransactionStatus', models.DO_NOTHING, db_column='status_code')
    receipt_serial = models.CharField(max_length=80, blank=True, null=True)
    receipt_attempt = models.IntegerField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'vendors_vendortransaction'

    def __str__(self):
        return self.name

