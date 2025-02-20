"""Модели для управления заказами в кафе."""
from django.db import models
from django.utils import timezone
from django.conf import settings
import json
from typing import List, Optional


class Dish:
    """Класс для представления блюда, загружаемого из JSON."""
    def __init__(self, id: int, name: str, price: float, description: Optional[str] = None):
        self.id = id
        self.name = name
        self.price = price
        self.description = description or ""

    def __str__(self) -> str:
        return f"{self.name} - {self.price}"

    @staticmethod
    def load_dishes() -> List['Dish']:
        """Загружает список блюд из JSON-файла."""
        json_path = f"{settings.BASE_DIR}/static/orders/dishes.json"
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                dishes_data = json.load(f)
                if not isinstance(dishes_data, list):
                    return []
                return [Dish(**dish) for dish in dishes_data if isinstance(dish, dict)]
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return []

    @staticmethod
    def get_by_id(dish_id: int) -> Optional['Dish']:
        """Получает блюдо по ID."""
        dishes = Dish.load_dishes()
        return next((dish for dish in dishes if dish.id == dish_id), None)


class Order(models.Model):
    """Модель заказа в кафе."""
    STATUS_CHOICES = [
        ('waiting', 'В ожидании'),
        ('ready', 'Готово'),
        ('paid', 'Оплачено'),
    ]

    table_number = models.PositiveIntegerField(verbose_name='Номер стола')
    dishes = models.JSONField(default=list, verbose_name='Блюда')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Общая стоимость')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting', verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата оплаты')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'Заказ #{self.id} - Стол {self.table_number}'

    def calculate_total_price(self) -> None:
        """Рассчитывает общую стоимость заказа."""
        total = 0.00
        dishes = Dish.load_dishes()
        if not isinstance(self.dishes, list):
            self.dishes = []
        for dish_id in self.dishes:
            try:
                dish_id = int(dish_id)
                dish = Dish.get_by_id(dish_id)
                if dish:
                    total += dish.price
            except (ValueError, TypeError):
                continue
        self.total_price = total
        self.save()

    def mark_as_paid(self) -> None:
        """Отмечает заказ как оплаченный."""
        if self.status == 'paid' and not self.paid_at:
            self.paid_at = timezone.now()
            self.save()

    def get_dish_names(self) -> str:
        """Возвращает строку с названиями и ценами блюд."""
        all_dishes = {dish.id: dish for dish in Dish.load_dishes()}
        dish_names = []
        for dish_id in self.dishes:
            if isinstance(dish_id, int):
                dish = all_dishes.get(dish_id)
                if dish:
                    dish_names.append(f"{dish.name} - {dish.price:.2f}")
        return ', '.join(dish_names) if dish_names else 'Нет блюд'

    def is_table_number_unique(self):
        """Проверяет уникальность номера стола для активных заказов."""
        return not Order.objects.filter(
            table_number=self.table_number,
            status__in=['waiting', 'ready']
        ).exclude(pk=self.pk).exists()
