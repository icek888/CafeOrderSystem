"""Админ-панель для управления заказами в кафе."""
from django.contrib import admin

from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админ-панель для управления заказами."""
    list_display = ('id', 'table_number', 'total_price', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('table_number',)
    readonly_fields = ('created_at', 'total_price')

    def has_add_permission(self, request):
        """Отключаем добавление заказов через админку, если нужно."""
        return True