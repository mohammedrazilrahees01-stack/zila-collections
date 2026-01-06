from django.urls import path
from apps.orders.views import (
    checkout,
    order_success,
    my_orders,
    cancel_order,
    request_return,
    download_invoice,
    online_payment,
)

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('success/<int:order_id>/', order_success, name='order_success'),

    # Online payment
    path('payment/<int:order_id>/', online_payment, name='online_payment'),

    path('my-orders/', my_orders, name='my_orders'),
    path('cancel/<int:order_id>/', cancel_order, name='cancel_order'),
    path('return/<int:order_id>/', request_return, name='request_return'),
    path('invoice/<int:order_id>/', download_invoice, name='download_invoice'),
]
