from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.models import User

from .models import Order, Coupon, ReturnRequest


# =====================================================
# SHOPKEEPER ACCESS DECORATOR
# =====================================================
def shopkeeper_only(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('customer_login')

        if request.user.email != 'zila@admin.com':
            return redirect('customer_home')

        return view_func(request, *args, **kwargs)
    return _wrapped_view


# =====================================================
# SHOPKEEPER: ALL ORDERS
# =====================================================
@login_required
@shopkeeper_only
def shopkeeper_orders(request):
    orders = (
        Order.objects
        .select_related('user')
        .prefetch_related('items')
        .order_by('-created_at')
    )
    return render(request, 'shopkeeper/orders.html', {'orders': orders})


# =====================================================
# SHOPKEEPER: ORDER DETAIL
# =====================================================
@login_required
@shopkeeper_only
def shopkeeper_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shopkeeper/order_detail.html', {'order': order})


# =====================================================
# SHOPKEEPER: VERIFY PAYMENT (STRICT & IDEMPOTENT)
# =====================================================
@login_required
@shopkeeper_only
@transaction.atomic
def verify_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Already resolved
    if order.payment_status == 'PAID':
        return redirect('shopkeeper_order_detail', order_id=order.id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            order.payment_status = 'PAID'
            if order.status == 'pending':
                order.status = 'packed'

        elif action == 'reject':
            order.payment_status = 'NOT PAID'
            order.status = 'cancelled'

        order.save()

    return redirect('shopkeeper_order_detail', order_id=order.id)


# =====================================================
# SHOPKEEPER: UPDATE ORDER STATUS (STATE MACHINE)
# =====================================================
@login_required
@shopkeeper_only
@transaction.atomic
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Immutable states
    if order.status in ['cancelled', 'delivered']:
        return redirect('shopkeeper_order_detail', order_id=order.id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        valid_flow = {
            'pending': ['packed'],
            'packed': ['shipped'],
            'shipped': ['delivered'],
        }

        allowed_next = valid_flow.get(order.status, [])

        if new_status not in allowed_next:
            return redirect('shopkeeper_order_detail', order_id=order.id)

        # ONLINE orders must be PAID
        if (
            order.payment_method == 'ONLINE'
            and order.payment_status != 'PAID'
        ):
            return redirect('shopkeeper_order_detail', order_id=order.id)

        order.status = new_status
        order.save()

    return redirect('shopkeeper_order_detail', order_id=order.id)


# =====================================================
# SHOPKEEPER: COUPONS
# =====================================================
@login_required
@shopkeeper_only
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

    return render(request, 'shopkeeper/coupons.html', {'coupons': coupons})


# =====================================================
# SHOPKEEPER: RETURNS & REFUNDS (ONCE ONLY)
# =====================================================
@login_required
@shopkeeper_only
@transaction.atomic
def update_return_status(request, return_id):
    return_request = get_object_or_404(ReturnRequest, id=return_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status not in ['approved', 'rejected', 'refunded']:
            return redirect('shopkeeper_returns')

        if return_request.status == new_status:
            return redirect('shopkeeper_returns')

        # Prevent double refund
        if return_request.status == 'refunded':
            return redirect('shopkeeper_returns')

        return_request.status = new_status

        if new_status == 'refunded':
            order = return_request.order
            order.payment_status = 'REFUNDED'
            order.save()

        return_request.save()

    return redirect('shopkeeper_returns')


# =====================================================
# SHOPKEEPER: RETURNS LIST
# =====================================================
@login_required
@shopkeeper_only
def shopkeeper_returns(request):
    returns = (
        ReturnRequest.objects
        .select_related('order', 'order__user')
        .order_by('-created_at')
    )
    return render(request, 'shopkeeper/returns.html', {'returns': returns})


# =====================================================
# SHOPKEEPER: CUSTOMERS
# =====================================================
@login_required
@shopkeeper_only
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


@login_required
@shopkeeper_only
def shopkeeper_customer_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(user=user).order_by('-created_at')

    return render(request, 'shopkeeper/customer_detail.html', {
        'customer': user,
        'orders': orders
    })
