import pytest

from orders.models import DeliveryStatus, FulfillmentMethod, PaymentStatus, TransactionStatus, TransactionType


@pytest.mark.django_db
def test_lookup_table_counts():
    assert TransactionStatus.objects.count() == 7
    assert PaymentStatus.objects.count() == 4
    assert DeliveryStatus.objects.count() == 5
    assert FulfillmentMethod.objects.count() == 3
    assert TransactionType.objects.count() == 3


@pytest.mark.django_db
def test_terminal_statuses():
    # At least one terminal status per type
    assert PaymentStatus.objects.filter(is_terminal=True).exists()
    assert DeliveryStatus.objects.filter(is_terminal=True).exists()
