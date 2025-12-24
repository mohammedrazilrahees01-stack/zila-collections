from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.products.models import ProductVariant

@login_required
def cart_detail(request):
    cart = request.session.get('cart', {})
    return render(request, 'customer/cart.html', {'cart': cart})


@login_required
def add_to_cart(request, variant_id):
    cart = request.session.get('cart', {})

    variant = ProductVariant.objects.get(id=variant_id)
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
    return redirect('cart_detail')


@login_required
def update_cart(request, variant_id):
    cart = request.session.get('cart', {})
    vid = str(variant_id)

    if vid in cart:
        qty = int(request.POST.get('quantity', 1))
        variant = ProductVariant.objects.get(id=variant_id)

        if qty <= variant.stock:
            cart[vid]['quantity'] = qty

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
