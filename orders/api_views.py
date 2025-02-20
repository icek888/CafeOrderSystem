"""API-представления для управления заказами."""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import datetime, date, time
from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD-операций с заказами."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        """Фильтрация заказов по номеру стола или статусу."""
        queryset = super().get_queryset()
        table_number = self.request.query_params.get('table_number', None)
        status = self.request.query_params.get('status', None)
        if table_number:
            queryset = queryset.filter(table_number=table_number)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @action(detail=False, methods=['get'])
    def revenue(self, request):
        """Расчет выручки за указанный период."""
        start_date_str = request.query_params.get('start_date', '')
        start_time_str = request.query_params.get('start_time', '09:00')
        end_date_str = request.query_params.get('end_date', '')
        end_time_str = request.query_params.get('end_time', '17:00')

        try:
            if start_date_str and end_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                start_time = datetime.strptime(start_time_str, '%H:%M').time()
                end_time = datetime.strptime(end_time_str, '%H:%M').time()

                start_datetime = datetime.combine(start_date, start_time)
                end_datetime = datetime.combine(end_date, end_time)

                if start_datetime > end_datetime:
                    raise ValueError("Дата начала должна быть раньше даты окончания.")
            else:
                start_datetime = datetime.combine(date.today(), time(9, 0))
                end_datetime = datetime.combine(date.today(), time(17, 0))

            start_datetime = timezone.make_aware(start_datetime)
            end_datetime = timezone.make_aware(end_datetime)

            paid_orders = Order.objects.filter(
                status='paid',
                paid_at__range=(start_datetime, end_datetime)
            )
            total_revenue = sum(order.total_price for order in paid_orders)
            serializer = self.get_serializer(paid_orders, many=True)

            return Response({
                'total_revenue': total_revenue,
                'orders': serializer.data,
                'start_datetime': start_datetime.isoformat(),
                'end_datetime': end_datetime.isoformat()
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
