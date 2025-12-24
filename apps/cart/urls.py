from django.urls import path
from .views import cart_detail, add_to_cart, update_cart, remove_from_cart

urlpatterns = [
    path('', cart_detail, name='cart_detail'),
    path('add/<int:variant_id>/', add_to_cart, name='add_to_cart'),
    path('update/<int:variant_id>/', update_cart, name='update_cart'),
    path('remove/<int:variant_id>/', remove_from_cart, name='remove_from_cart'),
]
