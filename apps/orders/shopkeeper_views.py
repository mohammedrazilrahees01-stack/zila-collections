from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Order, Coupon, ReturnRequest


# -------------------------
# SHOPKEEPER: ALL ORDERS
# -------------------------

@login_required
def all_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'shopkeeper/orders.html', {
        'orders': orders
    })


# -------------------------
# SHOPKEEPER: UPDATE STATUS
# -------------------------

@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        status = request.POST.get('status')

        if status in [
            'pending',
            'packed',
            'shipped',
            'delivered',
            'cancelled',
            'returned',
        ]:
            order.status = status
            order.save()

    return redirect('shopkeeper_orders')


# -------------------------
# SHOPKEEPER: COUPONS
# -------------------------

@login_required
def manage_coupons(request):
    coupons = Coupon.objects.all().order_by('-id')

    if request.method == 'POST':
        code = request.POST.get('code')
        discount = request.POST.get('discount')

        if code and discount:
            Coupon.objects.create(
                code=code.upper(),
                discount_percent=int(discount),
                active=True
            )

    return render(request, 'shopkeeper/coupons.html', {
        'coupons': coupons
    })


# ============================================================
# PHASE 12 — RETURNS & REFUNDS (ADDED, NOT REPLACING)
# ============================================================

# -------------------------
# SHOPKEEPER: VIEW RETURNS
# -------------------------

@login_required
def shopkeeper_returns(request):
    returns = ReturnRequest.objects.select_related(
        'order', 'order__user'
    ).order_by('-created_at')

    return render(request, 'shopkeeper/returns.html', {
        'returns': returns
    })


# -------------------------
# SHOPKEEPER: UPDATE RETURN STATUS
# -------------------------

@login_required
def update_return_status(request, return_id):
    return_request = get_object_or_404(ReturnRequest, id=return_id)

    if request.method == 'POST':
        status = request.POST.get('status')

        if status in ['approved', 'rejected', 'refunded']:
            return_request.status = status

            # COD manual refund marker
            if status == 'refunded':
                return_request.order.payment_status = 'REFUNDED (COD)'
                return_request.order.save()

            return_request.save()

    return redirect('shopkeeper_returns')
