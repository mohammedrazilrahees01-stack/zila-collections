from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse

from apps.products.models import ProductVariant
from .models import Order, OrderItem, Coupon, ReturnRequest
from .forms import CheckoutForm
from .utils import generate_invoice_pdf


# =========================
# CHECKOUT
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.products.models import ProductVariant
from .models import Order, OrderItem
from .forms import CheckoutForm


@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    # ❗ Block checkout ONLY if cart is empty
    if not cart:
        return redirect('cart:cart_detail')

    form = CheckoutForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():

        payment_method = form.cleaned_data['payment_method']

        # ------------------------
        # CREATE ORDER (INITIAL)
        # ------------------------
        order = Order.objects.create(
            user=request.user,
            full_name=form.cleaned_data['full_name'],
            phone=form.cleaned_data['phone'],
            address=form.cleaned_data['address'],
            payment_method=payment_method,
            payment_status='NOT PAID',
            status='pending'
        )

        # ------------------------
        # CREATE ORDER ITEMS
        # ------------------------
        for variant_id, item in cart.items():
            variant = get_object_or_404(ProductVariant, id=variant_id)

            # ❌ Stock safety
            if variant.stock < item['quantity']:
                return redirect('cart:cart_detail')

            # Reduce stock
            variant.stock -= item['quantity']
            variant.save()

            OrderItem.objects.create(
                order=order,
                variant=variant,
                quantity=item['quantity'],
                price=item['price']
            )

        # ------------------------
        # CLEAR CART (AFTER ORDER CREATED)
        # ------------------------
        request.session['cart'] = {}
        request.session.modified = True

        # ------------------------
        # PAYMENT FLOW CONTROL
        # ------------------------
        if payment_method == 'ONLINE':
            order.payment_status = 'PAYMENT UNDER REVIEW'
            order.save()
            return redirect('online_payment', order_id=order.id)

        # COD FLOW
        return redirect('order_success', order_id=order.id)

    # ------------------------
    # GET REQUEST
    # ------------------------
    return render(request, 'customer/checkout.html', {
        'form': form
    })

# =========================
# ONLINE PAYMENT PAGE
# =========================

@login_required
def online_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        order.payment_reference = request.POST.get('payment_reference')
        order.payment_screenshot = request.FILES.get('payment_screenshot')
        order.payment_status = 'PAYMENT UNDER REVIEW'
        order.save()

        return redirect('my_orders')

    return render(request, 'customer/online_payment.html', {
        'order': order
    })

# =========================
# CONFIRM PAYMENT

@login_required
def confirm_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        order.payment_reference = request.POST.get('payment_reference')
        order.payment_screenshot = request.FILES.get('payment_screenshot')
        order.payment_status = 'PAYMENT UNDER REVIEW'
        order.save()

        return redirect('order_success', order_id=order.id)

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

    if order.status in ['pending', 'packed']:
        order.status = 'cancelled'
        order.save()

    return redirect('my_orders')


# =========================
# RETURN ORDER
# =========================

@login_required
def request_return(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != 'delivered' or hasattr(order, 'return_request'):
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
# INVOICE
# =========================

@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if not request.user.is_staff and order.user != request.user:
        return redirect('home')

    pdf = generate_invoice_pdf(order)

    return FileResponse(
        pdf,
        as_attachment=True,
        filename=f"invoice_order_{order.id}.pdf"
    )
