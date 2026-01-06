from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from apps.orders.models import Order


# =====================================================
# SHOPKEEPER ACCESS DECORATOR (AUTHORITATIVE)
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
# SHOPKEEPER: ORDERS LIST
# =====================================================
@login_required
@shopkeeper_only
def shopkeeper_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'shopkeeper/orders.html', {
        'orders': orders
    })


# =====================================================
# SHOPKEEPER: ORDER DETAIL
# =====================================================
@login_required
@shopkeeper_only
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shopkeeper/order_detail.html', {
        'order': order
    })


# =====================================================
# SHOPKEEPER: APPROVE PAYMENT
# =====================================================
@login_required
@shopkeeper_only
def approve_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.payment_status = 'PAID'
    order.save()
    return redirect('shopkeeper_order_detail', order_id=order.id)


# =====================================================
# SHOPKEEPER: REJECT PAYMENT
# =====================================================
@login_required
@shopkeeper_only
def reject_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.payment_status = 'NOT PAID'
    order.payment_reference = ''
    order.payment_screenshot = None
    order.save()
    return redirect('shopkeeper_order_detail', order_id=order.id)


# =====================================================
# SHOPKEEPER: CUSTOMERS LIST
# =====================================================
@login_required
@shopkeeper_only
def customers_list(request):
    query = request.GET.get('q', '')
    customers = User.objects.filter(is_staff=False)

    if query:
        customers = customers.filter(
            username__icontains=query
        ) | customers.filter(
            email__icontains=query
        )

    return render(request, 'shopkeeper/customers.html', {
        'customers': customers,
        'query': query
    })
