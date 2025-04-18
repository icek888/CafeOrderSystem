from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orders/', include('orders.urls', namespace='orders_app')),
    path('', include('orders.urls', namespace='root_orders')),
]