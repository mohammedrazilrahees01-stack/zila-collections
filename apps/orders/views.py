from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from apps.products.models import ProductVariant


# ======================================================
# INTERNAL — CART SANITIZER (CRITICAL)
# ======================================================

def _sanitize_cart(request):
    """
    Ensures cart contains only:
    - active products
    - active variants
    - valid stock
    - latest price
    """
    cart = request.session.get('cart', {})
    updated = False

    for variant_id in list(cart.keys()):
        try:
            variant = ProductVariant.objects.select_related('product').get(id=variant_id)
        except ProductVariant.DoesNotExist:
            del cart[variant_id]
            updated = True
            continue

        # ❌ Product or variant inactive
        if not variant.is_active or not variant.product.is_active:
            del cart[variant_id]
            updated = True
            continue

        # ❌ Out of stock
        if variant.stock <= 0:
            del cart[variant_id]
            updated = True
            continue

        # 🔒 Cap quantity to stock
        if cart[variant_id]['quantity'] > variant.stock:
            cart[variant_id]['quantity'] = variant.stock
            updated = True

        # 🔒 Sync latest price
        latest_price = float(variant.product.price)
        if cart[variant_id]['price'] != latest_price:
            cart[variant_id]['price'] = latest_price
            updated = True

    if updated:
        request.session['cart'] = cart
        request.session.modified = True

    return cart


# ======================================================
# CART DETAIL
# ======================================================

def cart_detail(request):
    cart = _sanitize_cart(request)

    items = []
    total = 0

    for variant_id, item in cart.items():
        variant = get_object_or_404(ProductVariant, id=variant_id)
        item_total = item['price'] * item['quantity']
        total += item_total

        items.append({
            'variant': variant,
            'product': variant.product,
            'quantity': item['quantity'],
            'price': item['price'],
            'total': item_total,
        })

    return render(request, 'customer/cart.html', {
        'items': items,
        'total': total
    })


# ======================================================
# ADD TO CART (POST)
# ======================================================

@require_POST
def add_to_cart_post(request):
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))

    variant = get_object_or_404(
        ProductVariant,
        id=variant_id,
        is_active=True,
        product__is_active=True
    )

    if variant.stock <= 0:
        return redirect('product_detail', slug=variant.product.slug)

    cart = request.session.get('cart', {})

    current_qty = cart.get(str(variant_id), {}).get('quantity', 0)
    new_qty = min(current_qty + quantity, variant.stock)

    cart[str(variant_id)] = {
        'quantity': new_qty,
        'price': float(variant.product.price)
    }

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart:cart_detail')


# ======================================================
# ADD TO CART (LINK)
# ======================================================

def add_to_cart(request, variant_id):
    variant = get_object_or_404(
        ProductVariant,
        id=variant_id,
        is_active=True,
        product__is_active=True
    )

    if variant.stock <= 0:
        return redirect('product_detail', slug=variant.product.slug)

    cart = request.session.get('cart', {})

    current_qty = cart.get(str(variant_id), {}).get('quantity', 0)
    new_qty = min(current_qty + 1, variant.stock)

    cart[str(variant_id)] = {
        'quantity': new_qty,
        'price': float(variant.product.price)
    }

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart:cart_detail')


# ======================================================
# BUY NOW (SAFE)
# ======================================================

@require_POST
def buy_now(request):
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))

    variant = get_object_or_404(
        ProductVariant,
        id=variant_id,
        is_active=True,
        product__is_active=True
    )

    if variant.stock <= 0:
        return redirect('product_detail', slug=variant.product.slug)

    quantity = min(quantity, variant.stock)

    request.session['cart'] = {
        str(variant_id): {
            'quantity': quantity,
            'price': float(variant.product.price)
        }
    }

    request.session.modified = True
    return redirect('checkout')


# ======================================================
# QUANTITY CONTROLS
# ======================================================

def increase_quantity(request, variant_id):
    cart = _sanitize_cart(request)

    if str(variant_id) in cart:
        variant = get_object_or_404(ProductVariant, id=variant_id)
        cart[str(variant_id)]['quantity'] = min(
            cart[str(variant_id)]['quantity'] + 1,
            variant.stock
        )
        request.session.modified = True

    return redirect('cart:cart_detail')


def decrease_quantity(request, variant_id):
    cart = _sanitize_cart(request)

    if str(variant_id) in cart:
        cart[str(variant_id)]['quantity'] -= 1
        if cart[str(variant_id)]['quantity'] <= 0:
            del cart[str(variant_id)]
        request.session.modified = True

    return redirect('cart:cart_detail')


def remove_from_cart(request, variant_id):
    cart = request.session.get('cart', {})

    if str(variant_id) in cart:
        del cart[str(variant_id)]
        request.session.modified = True

    return redirect('cart:cart_detail')
