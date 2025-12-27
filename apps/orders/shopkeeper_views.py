from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Order, Coupon, ReturnRequest


# =====================================================
# SHOPKEEPER: DASHBOARD – ALL ORDERS
# =====================================================

@login_required
def shopkeeper_orders(request):
    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')
    return render(request, 'shopkeeper/orders.html', {
        'orders': orders
    })


# =====================================================
# SHOPKEEPER: ORDER DETAIL
# =====================================================

@login_required
def shopkeeper_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return render(request, 'shopkeeper/order_detail.html', {
        'order': order
    })


# =====================================================
# SHOPKEEPER: APPROVE / REJECT ONLINE PAYMENT
# =====================================================

@login_required
def verify_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            order.payment_status = 'PAID'
            order.status = 'packed'
            order.save()

        elif action == 'reject':
            order.payment_status = 'NOT PAID'
            order.status = 'cancelled'
            order.save()

    # 🔁 IMPORTANT: redirect back to same order detail
    return redirect('shopkeeper_order_detail', order_id=order.id)


# =====================================================
# SHOPKEEPER: UPDATE ORDER STATUS
# =====================================================

@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        # ❌ Prevent shipping unpaid ONLINE orders
        if order.payment_method == 'ONLINE' and order.payment_status != 'PAID':
            return redirect('shopkeeper_order_detail', order_id=order.id)

        allowed_statuses = [
            'pending', 'packed', 'shipped',
            'delivered', 'cancelled', 'returned'
        ]

        if new_status in allowed_statuses:
            order.status = new_status
            order.save()

    return redirect('shopkeeper_order_detail', order_id=order.id)


# =====================================================
# SHOPKEEPER: COUPONS
# =====================================================

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


# =====================================================
# SHOPKEEPER: RETURNS
# =====================================================

@login_required
def shopkeeper_returns(request):
    returns = ReturnRequest.objects.select_related(
        'order', 'order__user'
    ).order_by('-created_at')

    return render(request, 'shopkeeper/returns.html', {
        'returns': returns
    })


@login_required
def update_return_status(request, return_id):
    return_request = get_object_or_404(ReturnRequest, id=return_id)

    if request.method == 'POST':
        status = request.POST.get('status')

        if status in ['approved', 'rejected', 'refunded']:
            return_request.status = status

            if status == 'refunded':
                return_request.order.payment_status = 'REFUNDED (COD)'
                return_request.order.save()

            return_request.save()

    return redirect('shopkeeper_returns')


# =====================================================
# SHOPKEEPER: CUSTOMERS LIST
# =====================================================

@login_required
def shopkeeper_customers(request):
    query = request.GET.get('q', '')

    users = User.objects.filter(is_staff=False)

    if query:
        users = users.filter(
            username__icontains=query
        ) | users.filter(
            email__icontains=query
        )

    return render(request, 'shopkeeper/customers.html', {
        'customers': users,
        'query': query
    })


# =====================================================
# SHOPKEEPER: CUSTOMER DETAIL (ORDER HISTORY)
# =====================================================

@login_required
def shopkeeper_customer_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(user=user).order_by('-created_at')

    return render(request, 'shopkeeper/customer_detail.html', {
        'customer': user,
        'orders': orders
    })


from django.contrib.auth.models import User

@login_required
def customers_list(request):
    query = request.GET.get('q', '')

    customers = User.objects.filter(is_staff=False)

    if query:
        customers = customers.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    return render(request, 'shopkeeper/customers.html', {
        'customers': customers,
        'query': query
    })


@login_required
def shopkeeper_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return render(request, 'shopkeeper/order_detail.html', {
        'order': order
    })


@login_required
def verify_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            order.payment_status = 'PAID'
            order.status = 'packed'

        elif action == 'reject':
            order.payment_status = 'NOT PAID'
            order.status = 'cancelled'

        order.save()

    return redirect('shopkeeper_order_detail', order_id=order.id)
