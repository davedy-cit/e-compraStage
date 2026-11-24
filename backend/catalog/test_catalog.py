import pytest

from catalog.models import AvailabilityStatus, Category, Product, UnitOfMeasure, Vendor


@pytest.mark.django_db
def test_seed_counts():
    assert Product.objects.count() == 34
    assert Category.objects.count() == 9
    assert Vendor.objects.count() == 12
    assert UnitOfMeasure.objects.count() == 9
    assert AvailabilityStatus.objects.count() == 4


@pytest.mark.django_db
def test_tomato_price_comparison():
    rows = list(Product.objects.filter(name__istartswith="Tomato").order_by("price"))
    assert [r.price for r in rows] == [75, 78, 80]


@pytest.mark.django_db
def test_vendor_products_relation():
    villamor = Vendor.objects.get(name__contains="Villamor")
    assert villamor.product_set.count() >= 3  # seeded products
