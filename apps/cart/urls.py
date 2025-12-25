from django.urls import path
from .views import (
    cart_detail,
    add_to_cart,
    increase_quantity,
    decrease_quantity,
    remove_from_cart,
)

urlpatterns = [
    path('', cart_detail, name='cart_detail'),
    path('add/<int:variant_id>/', add_to_cart),
    path('increase/<int:variant_id>/', increase_quantity),
    path('decrease/<int:variant_id>/', decrease_quantity),
    path('remove/<int:variant_id>/', remove_from_cart),
]
