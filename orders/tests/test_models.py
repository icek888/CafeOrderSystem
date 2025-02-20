import pytest
from django.utils import timezone
from orders.models import Order


@pytest.mark.django_db
def test_order_creation(dishes_json):
    order = Order.objects.create(table_number=1, dishes=[1], status='waiting')
    assert order.id is not None
    assert order.table_number == 1
    assert order.dishes == [1]
    assert order.status == 'waiting'
    assert order.created_at is not None


@pytest.mark.django_db
def test_calculate_total_price(dishes_json):
    order = Order.objects.create(table_number=1, dishes=[1, 2])
    order.calculate_total_price()
    assert float(order.total_price) == 25.50


@pytest.mark.django_db
def test_mark_as_paid(dishes_json):
    order = Order.objects.create(table_number=1, dishes=[1], status='paid')
    order.mark_as_paid()
    assert order.paid_at is not None
    assert order.paid_at <= timezone.now()


@pytest.mark.django_db
def test_get_dish_names(dishes_json):
    order = Order.objects.create(table_number=1, dishes=[1, 2])
    dish_names = order.get_dish_names()
    assert dish_names == "Pizza - 15.00, Coffee - 10.50"


@pytest.mark.django_db
def test_is_table_number_unique(dishes_json):
    Order.objects.create(table_number=1, dishes=[1], status='waiting')
    order = Order(table_number=1, dishes=[2], status='ready')
    assert not order.is_table_number_unique()
    order.table_number = 2
    assert order.is_table_number_unique()