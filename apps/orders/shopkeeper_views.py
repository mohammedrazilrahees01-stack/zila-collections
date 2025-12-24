from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order

@login_required
def all_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'shopkeeper/orders.html', {'orders': orders})


@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    status = request.POST.get('status')
    if status:
        order.status = status
        if status == 'delivered':
            order.payment_status = 'PAID'
        order.save()
    return redirect('shopkeeper_orders')
