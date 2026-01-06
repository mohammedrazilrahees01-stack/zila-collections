from django.urls import path
from .views import (

    # CUSTOMER
    product_list,
    product_detail,
    add_review,

    # SHOPKEEPER – PRODUCTS
    shopkeeper_products,
    add_product,
    edit_product,
    toggle_product,

    # SHOPKEEPER – VARIANTS
    add_variant,
    edit_variant,
    toggle_variant,

    # SHOPKEEPER – IMAGES
    add_product_image,
    delete_product_image,
    set_primary_image,

    # SHOPKEEPER – CATEGORY
    add_category,
    edit_category,

    # SHOPKEEPER – REVIEWS
    manage_reviews,
)

urlpatterns = [

    # ======================
    # CUSTOMER
    # ======================
    path('', product_list, name='product_list'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('product/<int:product_id>/review/', add_review, name='add_review'),

    # ======================
    # SHOPKEEPER — PRODUCTS
    # ======================
    path('shopkeeper/', shopkeeper_products, name='shopkeeper_products'),
    path('shopkeeper/product/add/', add_product, name='add_product'),
    path('shopkeeper/product/<int:product_id>/edit/', edit_product, name='edit_product'),
    path('shopkeeper/product/<int:product_id>/toggle/', toggle_product, name='toggle_product'),

    # ======================
    # SHOPKEEPER — VARIANTS
    # ======================
    path('shopkeeper/product/<int:product_id>/variant/', add_variant, name='add_variant'),
    path('shopkeeper/variant/<int:variant_id>/edit/', edit_variant, name='edit_variant'),
    path('shopkeeper/variant/<int:variant_id>/toggle/', toggle_variant, name='toggle_variant'),

    # ======================
    # SHOPKEEPER — IMAGES
    # ======================
    path('shopkeeper/product/<int:product_id>/image/', add_product_image, name='add_product_image'),
    path('shopkeeper/image/<int:image_id>/delete/', delete_product_image, name='delete_product_image'),
    path('shopkeeper/image/<int:image_id>/primary/', set_primary_image, name='set_primary_image'),

    # ======================
    # SHOPKEEPER — CATEGORY
    # ======================
    path('shopkeeper/category/add/', add_category, name='add_category'),
    path('shopkeeper/category/<int:category_id>/edit/', edit_category, name='edit_category'),

    # ======================
    # SHOPKEEPER — REVIEWS
    # ======================
    path('shopkeeper/reviews/', manage_reviews, name='manage_reviews'),
]
