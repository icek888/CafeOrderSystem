"""URL-маршруты для приложения orders."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

router = DefaultRouter()
router.register(r'orders', api_views.OrderViewSet)

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('create/', views.order_create, name='order_create'),
    path('delete/<int:order_id>/', views.order_delete, name='order_delete'),
    path('update/<int:order_id>/', views.order_update, name='order_update'),
    path('revenue/', views.revenue_report, name='revenue_report'),
    path('api/', include(router.urls)),
]