from django.db import models

# Create your models here.

class AvailabilityStatus(models.Model):
    code = models.CharField(primary_key=True, max_length=24)
    description = models.CharField(max_length=120)
    sort_order = models.IntegerField()
    is_orderable = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'catalog_availabilitystatus'


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=80)
    slug = models.CharField(unique=True, max_length=80)
    is_active = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'catalog_category'


class ComparisonGroup(models.Model):
    code = models.CharField(primary_key=True, max_length=32)
    name = models.CharField(max_length=120)
    base_unit = models.ForeignKey('UnitOfMeasure', models.DO_NOTHING, db_column='base_unit')
    description = models.CharField(max_length=255)
    is_active = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'catalog_comparisongroup'


class ComparisonGroupUnit(models.Model):
    id = models.BigAutoField(primary_key=True)
    comparison_group = models.ForeignKey("ComparisonGroup", models.CASCADE, db_column='comparison_group')
    unit = models.ForeignKey('UnitOfMeasure', models.DO_NOTHING, db_column='unit')
    factor_to_base = models.DecimalField(max_digits=12, decimal_places=4)

    class Meta:
        managed = False
        db_table = 'catalog_comparisongroupunit'
        unique_together = (('comparison_group', 'unit'),)


class InventoryMovement(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey('Product', models.CASCADE)
    delta = models.IntegerField()
    reason_code = models.ForeignKey('InventoryReason', models.DO_NOTHING, db_column='reason_code')
    order = models.ForeignKey('orders.Order', models.SET_NULL, blank=True, null=True)
    note = models.CharField(max_length=255)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'catalog_inventorymovement'


class InventoryReason(models.Model):
    code = models.CharField(primary_key=True, max_length=24)
    description = models.CharField(max_length=120)
    direction = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'catalog_inventoryreason'


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    unit_code = models.ForeignKey('UnitOfMeasure', models.DO_NOTHING, db_column='unit_code')
    stall_location = models.CharField(max_length=120)
    availability_code = models.ForeignKey("AvailabilityStatus", models.DO_NOTHING, db_column='availability_code')
    stock_quantity = models.IntegerField()
    low_stock_threshold = models.IntegerField()
    category = models.ForeignKey("Category", models.DO_NOTHING)
    vendor = models.ForeignKey('Vendor', models.CASCADE)
    comparison_group = models.ForeignKey("ComparisonGroup", models.DO_NOTHING, db_column='comparison_group', blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'catalog_product'


class UnitOfMeasure(models.Model):
    code = models.CharField(primary_key=True, max_length=16)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255)
    is_active = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'catalog_unitofmeasure'


class Vendor(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=150)
    stall_location = models.CharField(max_length=120)
    market_section = models.CharField(max_length=120)
    contact_phone = models.CharField(max_length=32)
    contact_email = models.CharField(max_length=254)
    is_active = models.IntegerField()
    user = models.OneToOneField('accounts.AuthUser', models.DO_NOTHING)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'catalog_vendor'

    def __str__(self):
        return self.name

