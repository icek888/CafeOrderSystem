import pytest
from django.urls import reverse
from orders.models import Order


@pytest.mark.django_db
def test_order_list_view(auth_client, sample_order):
    response = auth_client.get(reverse('orders:order_list'))
    assert response.status_code == 200
    assert 'orders_with_dishes' in response.context
    assert len(response.context['orders_with_dishes']) == 1


@pytest.mark.django_db
def test_order_create_view_get(auth_client):
    response = auth_client.get(reverse('orders:order_create'))
    assert response.status_code == 200
    assert 'form' in response.context


@pytest.mark.django_db
def test_order_create_view_post_valid(auth_client, dishes_json):
    data = {'table_number': 1, 'dishes': ['1', '2'], 'status': 'waiting'}
    response = auth_client.post(reverse('orders:order_create'), data)
    assert response.status_code == 302
    assert Order.objects.count() == 1


@pytest.mark.django_db
def test_order_update_view_post_valid(auth_client, sample_order):
    data = {'table_number': 2, 'dishes': ['2'], 'status': 'ready'}
    response = auth_client.post(reverse('orders:order_update', args=[sample_order.id]), data)
    assert response.status_code == 302
    sample_order.refresh_from_db()
    assert sample_order.table_number == 2
    assert sample_order.dishes == [2]
    assert sample_order.status == 'ready'


@pytest.mark.django_db
def test_order_delete_view(auth_client, sample_order):
    response = auth_client.post(reverse('orders:order_delete', args=[sample_order.id]))
    assert response.status_code == 302
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_revenue_report_view(auth_client, sample_order):
    sample_order.status = 'paid'
    sample_order.mark_as_paid()
    sample_order.save()
    response = auth_client.get(reverse('orders:revenue_report'), {
        'start_date': '2025-02-20',
        'end_date': '2025-02-20',
        'start_time': '00:00',
        'end_time': '23:59'
    })
    assert response.status_code == 200
    assert 'total_revenue' in response.context
    assert float(response.context['total_revenue']) == 25.50
