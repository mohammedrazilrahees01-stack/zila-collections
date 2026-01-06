from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Sum, Count, F
from datetime import timedelta
from django.utils import timezone

from .models import Order, OrderItem


@login_required
def analytics_dashboard(request):
    if request.user.email != 'zila@admin.com':
        return redirect('customer_home')

    orders = Order.objects.all()

    total_orders = orders.count()
    delivered_orders = orders.filter(status='delivered').count()
    pending_orders = orders.filter(status='pending').count()
    returned_orders = orders.filter(status='returned').count()

    total_revenue = OrderItem.objects.filter(
        order__payment_status='PAID'
    ).aggregate(
        revenue=Sum(F('price') * F('quantity'))
    )['revenue'] or 0

    last_7_days = timezone.now() - timedelta(days=7)
    last_30_days = timezone.now() - timedelta(days=30)

    revenue_7_days = OrderItem.objects.filter(
        order__payment_status='PAID',
        order__created_at__gte=last_7_days
    ).aggregate(
        revenue=Sum(F('price') * F('quantity'))
    )['revenue'] or 0

    revenue_30_days = OrderItem.objects.filter(
        order__payment_status='PAID',
        order__created_at__gte=last_30_days
    ).aggregate(
        revenue=Sum(F('price') * F('quantity'))
    )['revenue'] or 0

    context = {
        'total_orders': total_orders,
        'delivered_orders': delivered_orders,
        'pending_orders': pending_orders,
        'returned_orders': returned_orders,
        'total_revenue': total_revenue,
        'revenue_7_days': revenue_7_days,
        'revenue_30_days': revenue_30_days,
    }

    return render(request, 'shopkeeper/analytics.html', context)
