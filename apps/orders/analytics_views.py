from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count, F
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone

from .models import Order, OrderItem


@login_required
def analytics_dashboard(request):
    orders = Order.objects.all()
    paid_orders = orders.filter(payment_status='PAID')

    # --------------------
    # ORDER COUNTS
    # --------------------
    total_orders = orders.count()
    delivered_orders = orders.filter(status='delivered').count()
    pending_orders = orders.filter(status='pending').count()
    returned_orders = orders.filter(status='returned').count()

    # --------------------
    # REVENUE (CORRECT)
    # --------------------
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

    # --------------------
    # TOP PRODUCTS
    # --------------------
    top_products = OrderItem.objects.filter(
        order__payment_status='PAID'
    ).values(
        'variant__product__name'
    ).annotate(
        quantity_sold=Sum('quantity'),
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-revenue')[:5]

    # --------------------
    # TOP CUSTOMERS
    # --------------------
    top_customers = OrderItem.objects.filter(
        order__payment_status='PAID'
    ).values(
        'order__user__email'
    ).annotate(
        orders=Count('order', distinct=True),
        total_spent=Sum(F('price') * F('quantity'))
    ).order_by('-total_spent')[:5]

    context = {
        'total_orders': total_orders,
        'delivered_orders': delivered_orders,
        'pending_orders': pending_orders,
        'returned_orders': returned_orders,

        'total_revenue': total_revenue,
        'revenue_7_days': revenue_7_days,
        'revenue_30_days': revenue_30_days,

        'top_products': top_products,
        'top_customers': top_customers,
    }

    return render(request, 'shopkeeper/analytics.html', context)
