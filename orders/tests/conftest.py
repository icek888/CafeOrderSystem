import pytest
import json
import os
from django.core.files import File
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from orders.models import Order, Dish
from django.conf import settings


@pytest.fixture
def dishes_json(tmp_path):
    """Фикстура для создания временного dishes.json."""
    dishes_data = [
        {"id": 1, "name": "Pizza", "price": 15.00},
        {"id": 2, "name": "Coffee", "price": 10.50}
    ]
    json_path = tmp_path / "dishes.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(dishes_data, f)
    
    original_path = settings.BASE_DIR / "static" / "orders" / "dishes.json"
    os.makedirs(os.path.dirname(original_path), exist_ok=True)
    with open(original_path, 'w', encoding='utf-8') as f:
        json.dump(dishes_data, f)
    yield json_path
    if os.path.exists(original_path):
        os.remove(original_path)


@pytest.fixture
def auth_user():
    """Фикстура для создания авторизованного пользователя."""
    user = User.objects.create_user(username='testuser', password='testpass')
    return user


@pytest.fixture
def auth_client(auth_user, client):
    """Фикстура для авторизованного клиента Django."""
    client.login(username='testuser', password='testpass')
    return client


@pytest.fixture
def api_client_with_token(auth_user):
    """Фикстура для авторизованного API-клиента с токеном."""
    token, _ = Token.objects.get_or_create(user=auth_user)
    api_client = APIClient()
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client


@pytest.fixture
def sample_order(dishes_json):
    """Фикстура для создания тестового заказа."""
    order = Order.objects.create(table_number=1, dishes=[1, 2], status='waiting')
    order.calculate_total_price()
    return order