from django.urls import path
from .shopkeeper_views import (
    all_orders,
    update_order_status,
    manage_coupons,
    shopkeeper_returns,
    update_return_status,
)

urlpatterns = [
    path('', all_orders, name='shopkeeper_orders'),
    path('update/<int:order_id>/', update_order_status, name='update_order_status'),
    path('coupons/', manage_coupons, name='manage_coupons'),

    # Phase 12
    path('returns/', shopkeeper_returns, name='shopkeeper_returns'),
    path('returns/update/<int:return_id>/', update_return_status, name='update_return_status'),
]
