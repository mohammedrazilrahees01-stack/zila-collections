from django.urls import path
from .views import (
    cart_detail,
    add_to_cart,
    add_to_cart_post,
    buy_now,
    increase_quantity,
    decrease_quantity,
    remove_from_cart,
)

app_name = 'cart'

urlpatterns = [
    path('', cart_detail, name='cart_detail'),

    # Add to cart (POST)
    path('add/', add_to_cart_post, name='add_to_cart_post'),

    # Buy now
    path('buy-now/', buy_now, name='buy_now'),

    # Variant operations
    path('add/<int:variant_id>/', add_to_cart, name='add_to_cart'),
    path('increase/<int:variant_id>/', increase_quantity, name='increase_quantity'),
    path('decrease/<int:variant_id>/', decrease_quantity, name='decrease_quantity'),
    path('remove/<int:variant_id>/', remove_from_cart, name='remove_from_cart'),
]
