from django.urls import path
from .shopkeeper_views import (
    shopkeeper_orders,
    shopkeeper_order_detail,
    verify_payment,
    update_order_status,
    manage_coupons,
    shopkeeper_returns,
    update_return_status,
    shopkeeper_customers,
    shopkeeper_customer_detail,
)

urlpatterns = [

    # Orders
    path('', shopkeeper_orders, name='shopkeeper_orders'),
    path('order/<int:order_id>/', shopkeeper_order_detail, name='shopkeeper_order_detail'),
    path('order/<int:order_id>/payment/', verify_payment, name='verify_payment'),
    path('order/<int:order_id>/status/', update_order_status, name='update_order_status'),

    # Customers
    path('customers/', shopkeeper_customers, name='shopkeeper_customers'),
    path('customers/<int:user_id>/', shopkeeper_customer_detail, name='shopkeeper_customer_detail'),

    # Coupons
    path('coupons/', manage_coupons, name='manage_coupons'),

    # Returns
    path('returns/', shopkeeper_returns, name='shopkeeper_returns'),
    path('returns/update/<int:return_id>/', update_return_status, name='update_return_status'),
]
