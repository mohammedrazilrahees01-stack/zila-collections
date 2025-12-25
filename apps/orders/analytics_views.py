from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils.timezone import now, timedelta

from .models import Order, OrderItem


@login_required
def analytics_dashboard(request):
    today = now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)

    # -----------------------
    # BASIC COUNTS
    # -----------------------
    total_orders = Order.objects.count()

    delivered_orders = Order.objects.filter(status='delivered').count()
    pending_orders = Order.objects.filter(status__in=['pending', 'packed']).count()
    returned_orders = Order.objects.filter(status='returned').count()

    # -----------------------
    # REVENUE
    # -----------------------
    total_revenue = sum(
        order.final_total() for order in
        Order.objects.filter(status='delivered')
    )

    revenue_7_days = sum(
        order.final_total() for order in
        Order.objects.filter(created_at__date__gte=last_7_days)
    )

    revenue_30_days = sum(
        order.final_total() for order in
        Order.objects.filter(created_at__date__gte=last_30_days)
    )

    # -----------------------
    # TOP PRODUCTS
    # -----------------------
    top_products = (
        OrderItem.objects
        .values('variant__product__name')
        .annotate(
            sold_qty=Sum('quantity'),
            revenue=Sum('price')
        )
        .order_by('-sold_qty')[:5]
    )

    # -----------------------
    # TOP CUSTOMERS
    # -----------------------
    top_customers = (
        Order.objects
        .values('user__username')
        .annotate(
            total_spent=Sum('items__price'),
            orders=Count('id')
        )
        .order_by('-total_spent')[:5]
    )

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
