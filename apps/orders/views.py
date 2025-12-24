from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.products.models import ProductVariant
from .models import Order, OrderItem
from .forms import CheckoutForm

@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart_detail')

    form = CheckoutForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        order = Order.objects.create(
            user=request.user,
            full_name=form.cleaned_data['full_name'],
            phone=form.cleaned_data['phone'],
            address=form.cleaned_data['address'],
        )

        for key, item in cart.items():
            variant = ProductVariant.objects.get(id=key)

            # stock reduction
            if variant.stock >= item['quantity']:
                variant.stock -= item['quantity']
                variant.save()

                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    quantity=item['quantity'],
                    price=item['price']
                )

        request.session['cart'] = {}
        request.session.modified = True

        return redirect('order_success', order_id=order.id)

    return render(request, 'customer/checkout.html', {'form': form})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'customer/order_success.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'customer/my_orders.html', {'orders': orders})


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status in ['pending', 'packed']:
        order.status = 'cancelled'
        order.save()
    return redirect('my_orders')
