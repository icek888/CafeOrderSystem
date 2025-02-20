"""Представления для управления заказами в кафе."""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib import messages
from .models import Order
from .forms import OrderForm
from datetime import datetime, date, time
from django.utils import timezone


def order_list(request):
    """Отображение списка всех заказов с возможностью поиска по номеру стола или статусу."""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    orders = Order.objects.all()
    if query:
        orders = orders.filter(table_number__icontains=query)
    if status:
        orders = orders.filter(status=status)

    orders_with_dishes = [
        {'order': order, 'dish_names': order.get_dish_names()} for order in orders
    ]
    messages.info(
        request,
        f'Список заказов загружен. Поиск: запрос "{query}", статус "{status}".'
    )
    return render(
        request,
        'orders/order_list.html',
        {'orders_with_dishes': orders_with_dishes, 'query': query, 'status': status}
    )


def order_create(request):
    """Создание нового заказа."""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                order = form.save()
                messages.success(request, 'Заказ успешно создан!')
                messages.info(
                    request,
                    f'Общая стоимость заказа: {order.total_price}, статус: '
                    f'{order.status}, paid_at: {order.paid_at}'
                )
                return redirect('orders:order_list')
            except Exception as e:
                messages.error(
                    request,
                    f'Неизвестная ошибка при создании заказа: {str(e)}'
                )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request,
                        f'Ошибка в поле "{form.fields[field].label}": {error}'
                    )
    else:
        form = OrderForm()
    messages.info(request, 'Готов к созданию нового заказа.')
    return render(request, 'orders/order_create.html', {'form': form})


def order_delete(request, order_id: int):
    """Удаление заказа по ID с обработкой несуществующих заказов."""
    try:
        order = get_object_or_404(Order, id=order_id)
    except Http404:
        messages.error(
            request,
            f'Заказ с ID {order_id} не найден. Проверьте введенные данные.'
        )
        return redirect('orders:order_list')

    if request.method == 'POST':
        try:
            order.delete()
            messages.success(request, 'Заказ успешно удален!')
            messages.info(
                request,
                f'Удален заказ #{order.id} для стола {order.table_number}.'
            )
            return redirect('orders:order_list')
        except Exception as e:
            messages.error(
                request,
                f'Ошибка при удалении заказа: {str(e)}'
            )
            return redirect('orders:order_list')
    return render(request, 'orders/order_delete.html', {'order': order})


def order_update(request, order_id: int):
    """Обновление заказа."""
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            try:
                order = form.save()
                messages.success(request, 'Заказ успешно обновлен!')
                messages.info(
                    request,
                    f'Обновлен заказ #{order.id}, новая стоимость: '
                    f'{order.total_price}, статус: {order.status}, '
                    f'paid_at: {order.paid_at}'
                )
                return redirect('orders:order_list')
            except Exception as e:
                messages.error(
                    request,
                    f'Неизвестная ошибка при обновлении заказа: {str(e)}'
                )
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request,
                        f'Ошибка в поле "{form.fields[field].label}": {error}'
                    )
    else:
        form = OrderForm(instance=order)
    messages.info(request, f'Редактирование заказа #{order.id}.')
    return render(
        request,
        'orders/order_update.html',
        {'form': form, 'order': order}
    )


def revenue_report(request):
    """Отчет о выручке за указанный диапазон времени для заказов со статусом 'оплачено'."""
    start_date_str = request.GET.get('start_date', '')
    start_time_str = request.GET.get('start_time', '09:00')
    end_date_str = request.GET.get('end_date', '')
    end_time_str = request.GET.get('end_time', '17:00')

    try:
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()

            start_datetime = datetime.combine(start_date, start_time)
            end_datetime = datetime.combine(end_date, end_time)

            if start_datetime > end_datetime:
                messages.error(
                    request,
                    'Дата и время начала должны быть раньше даты и времени окончания.'
                )
                start_datetime = datetime.combine(date.today(), time(9, 0))
                end_datetime = datetime.combine(date.today(), time(17, 0))
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

        paid_orders_with_dishes = [
            {'order': order, 'dish_names': order.get_dish_names()} for order in paid_orders
        ]

        messages.info(
            request,
            f'Отчет о выручке за период с {start_datetime} по {end_datetime}: '
            f'{len(paid_orders)} оплаченных заказов.'
        )
        return render(
            request,
            'orders/revenue_report.html',
            {
                'total_revenue': total_revenue,
                'paid_orders_with_dishes': paid_orders_with_dishes,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'start_date': start_datetime.date().isoformat(),
                'start_time': start_datetime.strftime('%H:%M'),
                'end_date': end_datetime.date().isoformat(),
                'end_time': end_datetime.strftime('%H:%M'),
            }
        )
    except ValueError as e:
        messages.error(
            request,
            f'Некорректный формат даты или времени: {str(e)}'
        )
        start_datetime = timezone.make_aware(datetime.combine(date.today(), time(9, 0)))
        end_datetime = timezone.make_aware(datetime.combine(date.today(), time(17, 0)))
        paid_orders = Order.objects.filter(
            status='paid',
            paid_at__range=(start_datetime, end_datetime)
        )
        total_revenue = sum(order.total_price for order in paid_orders)
        paid_orders_with_dishes = [
            {'order': order, 'dish_names': order.get_dish_names()} for order in paid_orders
        ]
        return render(
            request,
            'orders/revenue_report.html',
            {
                'total_revenue': total_revenue,
                'paid_orders_with_dishes': paid_orders_with_dishes,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'start_date': start_datetime.date().isoformat(),
                'start_time': start_datetime.strftime('%H:%M'),
                'end_date': end_datetime.date().isoformat(),
                'end_time': end_datetime.strftime('%H:%M'),
            }
        )
