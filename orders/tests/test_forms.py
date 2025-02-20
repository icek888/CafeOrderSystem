import pytest
from orders.forms import OrderForm
from orders.models import Order


@pytest.mark.django_db
def test_order_form_valid(dishes_json):
    form_data = {'table_number': 1, 'dishes': ['1', '2'], 'status': 'waiting'}
    form = OrderForm(data=form_data)
    assert form.is_valid()
    order = form.save()
    assert order.table_number == 1
    assert order.dishes == [1, 2]
    assert float(order.total_price) == 25.50


@pytest.mark.django_db
def test_order_form_invalid_table_number(dishes_json):
    form_data = {'table_number': 0, 'dishes': ['1'], 'status': 'waiting'}
    form = OrderForm(data=form_data)
    assert not form.is_valid()
    assert 'table_number' in form.errors


@pytest.mark.django_db
def test_order_form_duplicate_table_number(dishes_json):
    Order.objects.create(table_number=1, dishes=[1], status='waiting')
    form_data = {'table_number': 1, 'dishes': ['2'], 'status': 'waiting'}
    form = OrderForm(data=form_data)
    assert not form.is_valid()
    assert 'table_number' in form.errors


@pytest.mark.django_db
def test_order_form_invalid_dishes(dishes_json):
    form_data = {'table_number': 1, 'dishes': ['999'], 'status': 'waiting'}
    form = OrderForm(data=form_data)
    assert not form.is_valid()
    assert 'dishes' in form.errors