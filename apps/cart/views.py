from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.products.models import ProductVariant


@login_required
def cart_detail(request):
    cart = request.session.get('cart', {})
    return render(request, 'customer/cart.html', {'cart': cart})


@login_required
def add_to_cart(request, variant_id):
    cart = request.session.get('cart', {})
    variant = get_object_or_404(ProductVariant, id=variant_id)
    vid = str(variant_id)

    if vid in cart:
        if cart[vid]['quantity'] < variant.stock:
            cart[vid]['quantity'] += 1
    else:
        cart[vid] = {
            'name': variant.product.name,
            'variant': f"{variant.size}/{variant.color}",
            'price': float(variant.product.price),
            'quantity': 1,
        }

    request.session['cart'] = cart
    request.session.modified = True

    # Buy Now shortcut
    if request.GET.get('buy') == '1':
        return redirect('/orders/checkout/')

    return redirect('cart_detail')


@login_required
def increase_quantity(request, variant_id):
    cart = request.session.get('cart', {})
    vid = str(variant_id)

    if vid in cart:
        variant = get_object_or_404(ProductVariant, id=variant_id)
        if cart[vid]['quantity'] < variant.stock:
            cart[vid]['quantity'] += 1

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')


@login_required
def decrease_quantity(request, variant_id):
    cart = request.session.get('cart', {})
    vid = str(variant_id)

    if vid in cart:
        cart[vid]['quantity'] -= 1
        if cart[vid]['quantity'] <= 0:
            del cart[vid]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')


@login_required
def remove_from_cart(request, variant_id):
    cart = request.session.get('cart', {})
    vid = str(variant_id)

    if vid in cart:
        del cart[vid]

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')
