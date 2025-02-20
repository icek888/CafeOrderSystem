"""Формы для управления заказами в кафе."""
from django import forms
from django.core.exceptions import ValidationError
from .models import Order, Dish


class OrderForm(forms.ModelForm):
    """Форма для создания и редактирования заказа."""
    dishes = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
        label='Существующие блюда',
        required=False,
    )

    class Meta:
        model = Order
        fields = ['table_number', 'dishes', 'status']
        widgets = {
            'table_number': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dishes'].choices = [(str(dish.id), f"{dish.name} - {dish.price}") for dish in Dish.load_dishes()]

    def clean_table_number(self):
        table_number = self.cleaned_data['table_number']
        if table_number <= 0:
            raise ValidationError('Номер стола должен быть положительным числом.')
        instance = self.instance if self.instance.pk else None
        if Order.objects.filter(
            table_number=table_number,
            status__in=['waiting', 'ready']
        ).exclude(pk=instance.pk if instance else None).exists():
            raise ValidationError('Этот номер стола уже используется в активном заказе.')
        return table_number

    def clean_dishes(self):
        dish_ids = self.cleaned_data['dishes']
        valid_ids = {str(dish.id) for dish in Dish.load_dishes()}
        if dish_ids:
            invalid_ids = set(dish_ids) - valid_ids
            if invalid_ids:
                raise ValidationError(f'Некорректные ID блюд: {", ".join(invalid_ids)}')
        return [int(dish_id) for dish_id in dish_ids] if dish_ids else []

    def save(self, commit: bool = True) -> Order:
        instance = super().save(commit=False)
        instance.dishes = self.cleaned_data['dishes']
        if commit:
            instance.save()
            instance.calculate_total_price()
            if instance.status == 'paid' and not instance.paid_at:
                instance.mark_as_paid()
        return instance
