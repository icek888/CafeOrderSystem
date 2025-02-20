"""Сериализаторы для API управления заказами."""
from rest_framework import serializers
from .models import Order, Dish


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Order."""
    dish_names = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'table_number', 'dishes', 'total_price', 'status', 'created_at', 'paid_at', 'dish_names']
        read_only_fields = ['id', 'total_price', 'created_at', 'paid_at', 'dish_names']

    def get_dish_names(self, obj):
        """Получение названий блюд для заказа."""
        return obj.get_dish_names()

    def validate_table_number(self, value):
        """Проверка номера стола."""
        if value <= 0:
            raise serializers.ValidationError("Номер стола должен быть положительным числом.")
        instance = self.instance if self.instance else None
        if Order.objects.filter(
            table_number=value,
            status__in=['waiting', 'ready']
        ).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Этот номер стола уже используется в активном заказе.")
        return value

    def validate_dishes(self, value):
        """Проверка ID блюд."""
        valid_ids = {str(dish.id) for dish in Dish.load_dishes()}
        if value:
            invalid_ids = set(str(dish_id) for dish_id in value) - valid_ids
            if invalid_ids:
                raise serializers.ValidationError(f"Некорректные ID блюд: {', '.join(invalid_ids)}")
        return value

    def create(self, validated_data):
        """Создание нового заказа."""
        order = Order.objects.create(**validated_data)
        order.calculate_total_price()
        if order.status == 'paid':
            order.mark_as_paid()
        return order

    def update(self, instance, validated_data):
        """Обновление существующего заказа."""
        instance.table_number = validated_data.get('table_number', instance.table_number)
        instance.dishes = validated_data.get('dishes', instance.dishes)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        instance.calculate_total_price()
        if instance.status == 'paid' and not instance.paid_at:
            instance.mark_as_paid()
        return instance
