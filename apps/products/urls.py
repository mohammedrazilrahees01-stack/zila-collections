from django.urls import path
from .views import (
    product_list,
    product_detail,
    shopkeeper_products,
    add_category,
    add_product,
    add_variant,
    add_product_image,
)

urlpatterns = [
    # customer
    path('', product_list, name='product_list'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),

    # shopkeeper
    path('shopkeeper/', shopkeeper_products, name='shopkeeper_products'),
    path('shopkeeper/category/add/', add_category, name='add_category'),
    path('shopkeeper/product/add/', add_product, name='add_product'),
    path('shopkeeper/product/<int:product_id>/variant/', add_variant, name='add_variant'),
    path('shopkeeper/product/<int:product_id>/image/', add_product_image, name='add_product_image'),
]
