from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.db import transaction
from django.db.models import F

from .models import Order, OrderItem, ReturnRequest
from .forms import CheckoutForm
from .utils import generate_invoice_pdf
from apps.products.models import ProductVariant


# =========================
# CHECKOUT (CRITICAL)
# =========================
@login_required
@transaction.atomic
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart:cart_detail')

    form = CheckoutForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        # Prevent double submit
        if request.session.get('checkout_lock'):
            return redirect('cart:cart_detail')
        request.session['checkout_lock'] = True

        payment_method = form.cleaned_data['payment_method']

        order = Order.objects.create(
            user=request.user,
            full_name=form.cleaned_data['full_name'],
            phone=form.cleaned_data['phone'],
            address=form.cleaned_data['address'],
            payment_method=payment_method,
            payment_status='NOT PAID',
            status='pending'
        )

        for variant_id, item in cart.items():
            variant = ProductVariant.objects.select_for_update().get(id=variant_id)

            if variant.stock < item['quantity']:
                transaction.set_rollback(True)
                request.session['checkout_lock'] = False
                return redirect('cart:cart_detail')

            variant.stock = F('stock') - item['quantity']
            variant.save()

            OrderItem.objects.create(
                order=order,
                variant=variant,
                quantity=item['quantity'],
                price=item['price']
            )

        request.session['cart'] = {}
        request.session.modified = True
        request.session['checkout_lock'] = False

        if payment_method == 'ONLINE':
            order.payment_status = 'PAYMENT UNDER REVIEW'
            order.save()
            return redirect('online_payment', order_id=order.id)

        return redirect('order_success', order_id=order.id)

    return render(request, 'customer/checkout.html', {'form': form})


# =========================
# ONLINE PAYMENT
# =========================
@login_required
def online_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.payment_status in ['PAID', 'PAYMENT UNDER REVIEW']:
        return redirect('my_orders')

    if request.method == 'POST':
        order.payment_reference = request.POST.get('payment_reference')
        order.payment_screenshot = request.FILES.get('payment_screenshot')
        order.payment_status = 'PAYMENT UNDER REVIEW'
        order.save()
        return redirect('my_orders')

    return render(request, 'customer/online_payment.html', {'order': order})


# =========================
# ORDER SUCCESS
# =========================
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'customer/order_success.html', {'order': order})


# =========================
# MY ORDERS
# =========================
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'customer/my_orders.html', {'orders': orders})


# =========================
# CANCEL ORDER
# =========================
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.payment_status == 'PAID':
        return redirect('my_orders')

    if order.status not in ['pending', 'packed']:
        return redirect('my_orders')

    order.status = 'cancelled'
    order.save()
    return redirect('my_orders')


# =========================
# RETURN ORDER
# =========================
@login_required
def request_return(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != 'delivered':
        return redirect('my_orders')

    if hasattr(order, 'return_request'):
        return redirect('my_orders')

    if request.method == 'POST':
        ReturnRequest.objects.create(
            order=order,
            reason=request.POST.get('reason')
        )
        order.status = 'returned'
        order.save()
        return redirect('my_orders')

    return render(request, 'customer/request_return.html', {'order': order})


# =========================
# INVOICE DOWNLOAD
# =========================
@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user and request.user.email != 'zila@admin.com':
        return redirect('customer_home')

    pdf = generate_invoice_pdf(order)

    return FileResponse(
        pdf,
        as_attachment=True,
        filename=f"invoice_order_{order.id}.pdf"
    )
