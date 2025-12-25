from django.urls import path
from .views import checkout, order_success, my_orders, cancel_order, download_invoice
from .views import request_return

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('success/<int:order_id>/', order_success, name='order_success'),
    path('my-orders/', my_orders, name='my_orders'),
    path('cancel/<int:order_id>/', cancel_order, name='cancel_order'),
    path('return/<int:order_id>/', request_return, name='request_return'),
    path('invoice/<int:order_id>/', download_invoice, name='download_invoice'),
]
