from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from apps.products.models import ProductVariant


# -------------------------
# CART DETAIL
# -------------------------
def cart_detail(request):
    cart = request.session.get('cart', {})
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


# -------------------------
# ADD TO CART (POST)
# -------------------------
@require_POST
def add_to_cart_post(request):
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))

    variant = get_object_or_404(ProductVariant, id=variant_id)

    cart = request.session.get('cart', {})

    if str(variant_id) in cart:
        cart[str(variant_id)]['quantity'] += quantity
    else:
        cart[str(variant_id)] = {
            'quantity': quantity,
            'price': float(variant.product.price)
        }

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart:cart_detail')


# -------------------------
# ADD TO CART (LINK BASED)
# -------------------------
def add_to_cart(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart = request.session.get('cart', {})

    if str(variant_id) in cart:
        cart[str(variant_id)]['quantity'] += 1
    else:
        cart[str(variant_id)] = {
            'quantity': 1,
            'price': float(variant.product.price)
        }

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart:cart_detail')


# -------------------------
# BUY NOW (POST → CHECKOUT)
# -------------------------
@require_POST
def buy_now(request):
    variant_id = request.POST.get('variant_id')
    quantity = int(request.POST.get('quantity', 1))

    variant = get_object_or_404(ProductVariant, id=variant_id)

    request.session['cart'] = {
        str(variant_id): {
            'quantity': quantity,
            'price': float(variant.product.price)
        }
    }
    request.session.modified = True

    return redirect('checkout')


# -------------------------
# QUANTITY CONTROLS
# -------------------------
def increase_quantity(request, variant_id):
    cart = request.session.get('cart', {})
    if str(variant_id) in cart:
        cart[str(variant_id)]['quantity'] += 1
        request.session.modified = True
    return redirect('cart:cart_detail')


def decrease_quantity(request, variant_id):
    cart = request.session.get('cart', {})
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
