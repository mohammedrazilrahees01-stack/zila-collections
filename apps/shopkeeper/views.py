from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from apps.orders.models import Order


@login_required
def shopkeeper_orders(request):
    orders = Order.objects.all().order_by('-created_at')

    return render(request, 'shopkeeper/orders.html', {
        'orders': orders
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return render(request, 'shopkeeper/order_detail.html', {
        'order': order
    })


@login_required
def approve_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    order.payment_status = 'PAID'
    order.save()

    return redirect('shopkeeper_order_detail', order_id=order.id)


@login_required
def reject_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    order.payment_status = 'NOT PAID'
    order.payment_reference = ''
    order.payment_screenshot = None
    order.save()

    return redirect('shopkeeper_order_detail', order_id=order.id)


@login_required
def customers_list(request):
    query = request.GET.get('q', '')

    customers = User.objects.all()

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


def shopkeeper_only(view):
    def wrapper(request, *args, **kwargs):
        if request.user.email != 'zila@admin.com':
            return redirect('customer_home')
        return view(request, *args, **kwargs)
    return wrapper
