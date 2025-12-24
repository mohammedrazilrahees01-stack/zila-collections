from django.urls import path
from .shopkeeper_views import all_orders, update_order_status

urlpatterns = [
    path('', all_orders, name='shopkeeper_orders'),
    path('update/<int:order_id>/', update_order_status, name='update_order_status'),
]
