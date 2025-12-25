from django.db import models
from django.contrib.auth.models import User
from apps.products.models import ProductVariant


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    payment_method = models.CharField(max_length=20, default='COD')
    payment_status = models.CharField(max_length=20, default='NOT PAID')

    # ✅ Coupon information
    coupon_code = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )
    discount_percent = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    # ---------- CALCULATED VALUES ----------

    def subtotal(self):
        """
        Total after discount (sum of OrderItem.price * quantity)
        """
        return sum(
            item.price * item.quantity
            for item in self.items.all()
        )

    def original_total(self):
        """
        Total before discount (original product prices)
        """
        return sum(
            item.variant.product.price * item.quantity
            for item in self.items.all()
        )

    def discount_amount(self):
        """
        How much discount was applied
        """
        return self.original_total() - self.subtotal()

    def final_total(self):
        """
        Final payable amount (same as subtotal)
        """
        return self.subtotal()

    def total_items(self):
        return sum(
            item.quantity
            for item in self.items.all()
        )

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    # ✅ FINAL price per unit AFTER discount
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"Order {self.order.id} - {self.variant}"


class Coupon(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True
    )

    discount_percent = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class ReturnRequest(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('refunded', 'Refunded'),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='return_request'
    )

    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='requested'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return Request — Order #{self.order.id}"