from django.urls import path
from .views import (
    shopkeeper_orders,
    order_detail,
    approve_payment,
    reject_payment,
    customers_list,
)

urlpatterns = [
    path('orders/', shopkeeper_orders, name='shopkeeper_orders'),
    path('orders/<int:order_id>/', order_detail, name='shopkeeper_order_detail'),
    path('orders/<int:order_id>/approve/', approve_payment, name='approve_payment'),
    path('orders/<int:order_id>/reject/', reject_payment, name='reject_payment'),

    path('customers/', customers_list, name='shopkeeper_customers'),
]
