import pytest
from django.urls import reverse
from orders.models import Order


@pytest.mark.django_db
def test_api_list_orders(api_client_with_token, sample_order):
    url = reverse('orders:order-list')
    response = api_client_with_token.get(url)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['table_number'] == 1


@pytest.mark.django_db
def test_api_create_order(api_client_with_token, dishes_json):
    url = reverse('orders:order-list')
    data = {'table_number': 2, 'dishes': [1, 2], 'status': 'waiting'}
    response = api_client_with_token.post(url, data, format='json')
    assert response.status_code == 201
    assert Order.objects.count() == 1
    assert float(response.json()['total_price']) == 25.50


@pytest.mark.django_db
def test_api_update_order(api_client_with_token, sample_order):
    url = reverse('orders:order-detail', args=[sample_order.id])
    data = {'table_number': 2, 'dishes': [2], 'status': 'paid'}
    response = api_client_with_token.put(url, data, format='json')
    assert response.status_code == 200
    sample_order.refresh_from_db()
    assert sample_order.table_number == 2
    assert sample_order.dishes == [2]
    assert sample_order.status == 'paid'
    assert sample_order.paid_at is not None


@pytest.mark.django_db
def test_api_delete_order(api_client_with_token, sample_order):
    url = reverse('orders:order-detail', args=[sample_order.id])
    response = api_client_with_token.delete(url)
    assert response.status_code == 204
    assert Order.objects.count() == 0


@pytest.mark.django_db
def test_api_filter_orders(api_client_with_token, sample_order):
    Order.objects.create(table_number=2, dishes=[2], status='paid')
    url = reverse('orders:order-list') + '?table_number=1&status=waiting'
    response = api_client_with_token.get(url)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['table_number'] == 1


@pytest.mark.django_db
def test_api_revenue_report(api_client_with_token, sample_order):
    sample_order.status = 'paid'
    sample_order.mark_as_paid()
    sample_order.save()
    url = reverse('orders:order-revenue') + '?start_date=2025-02-20&end_date=2025-02-20&start_time=00:00&end_time=23:59'
    response = api_client_with_token.get(url)
    assert response.status_code == 200
    assert float(response.json()['total_revenue']) == 25.50
    assert len(response.json()['orders']) == 1