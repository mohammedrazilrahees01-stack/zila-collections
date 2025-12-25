from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.products.models import ProductVariant
from .models import Order, OrderItem, Coupon
from .forms import CheckoutForm


# ------------------------
# CUSTOMER: CHECKOUT
# ------------------------

@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    # Safety: cannot checkout empty cart
    if not cart:
        return redirect('cart_detail')

    form = CheckoutForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        # ------------------------
        # COUPON VALIDATION
        # ------------------------
        discount_percent = 0
        coupon_code = form.cleaned_data.get('coupon_code')

        if coupon_code:
            try:
                coupon = Coupon.objects.get(
                    code=coupon_code.upper(),
                    active=True
                )
                discount_percent = coupon.discount_percent
            except Coupon.DoesNotExist:
                discount_percent = 0

        # ------------------------
        # CREATE ORDER
        # ------------------------
        order = Order.objects.create(
            user=request.user,
            full_name=form.cleaned_data['full_name'],
            phone=form.cleaned_data['phone'],
            address=form.cleaned_data['address'],
            payment_method='COD',
            payment_status='NOT PAID',
            status='pending',
            coupon_code=coupon_code if coupon_code else '',
            discount_percent=discount_percent
        )

        # ------------------------
        # CREATE ORDER ITEMS
        # FINAL STOCK CHECK (CRITICAL)
        # ------------------------
        for variant_id, item in cart.items():
            variant = get_object_or_404(ProductVariant, id=variant_id)

            # Final race-condition protection
            if variant.stock < item['quantity']:
                return redirect('cart_detail')

            # Reduce stock
            variant.stock -= item['quantity']
            variant.save()

            # Apply discount per item
            price = float(item['price'])
            if discount_percent > 0:
                price = price - (price * discount_percent / 100)

            OrderItem.objects.create(
                order=order,
                variant=variant,
                quantity=item['quantity'],
                price=price
            )

        # ------------------------
        # CLEAR CART
        # ------------------------
        request.session['cart'] = {}
        request.session.modified = True

        return redirect('order_success', order_id=order.id)

    return render(
        request,
        'customer/checkout.html',
        {'form': form}
    )


# ------------------------
# CUSTOMER: ORDER SUCCESS
# ------------------------

@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )
    return render(
        request,
        'customer/order_success.html',
        {'order': order}
    )


# ------------------------
# CUSTOMER: MY ORDERS
# ------------------------

@login_required
def my_orders(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'customer/my_orders.html',
        {'orders': orders}
    )


# ------------------------
# CUSTOMER: CANCEL ORDER
# ------------------------

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # Only allowed before shipping
    if order.status in ['pending', 'packed']:
        order.status = 'cancelled'
        order.save()

    return redirect('my_orders')


@login_required
def request_return(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    # Only allow return after delivery
    if order.status != 'delivered':
        return redirect('my_orders')

    # Prevent duplicate return
    if hasattr(order, 'return_request'):
        return redirect('my_orders')

    if request.method == 'POST':
        reason = request.POST.get('reason')
        ReturnRequest.objects.create(
            order=order,
            reason=reason
        )
        order.status = 'returned'
        order.save()
        return redirect('my_orders')

    return render(
        request,
        'customer/request_return.html',
        {'order': order}
    )

from django.http import FileResponse
from .utils import generate_invoice_pdf


@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Security: customer sees only own invoice
    if not request.user.is_staff and order.user != request.user:
        return redirect('home')

    pdf = generate_invoice_pdf(order)

    return FileResponse(
        pdf,
        as_attachment=True,
        filename=f"invoice_order_{order.id}.pdf"
    )
