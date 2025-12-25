from django.urls import path
from .views import wishlist_view, add_to_wishlist, remove_from_wishlist

urlpatterns = [
    path('', wishlist_view, name='wishlist'),
    path('add/<int:variant_id>/', add_to_wishlist),
    path('remove/<int:variant_id>/', remove_from_wishlist),
]
