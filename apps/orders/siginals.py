from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .email_utils import send_customer_email, send_shopkeeper_email


@receiver(post_save, sender=Order)
def order_status_email(sender, instance, created, **kwargs):

    # ------------------
    # NEW ORDER
    # ------------------
    if created:
        send_customer_email(
            subject=f"Order #{instance.id} Confirmed",
            message=(
                f"Hi {instance.full_name},\n\n"
                f"Your order #{instance.id} has been placed successfully.\n"
                f"Total Amount: ₹{instance.final_total()}\n\n"
                f"Thank you for shopping with Zila Collections."
            ),
            to_email=instance.user.email
        )

        send_shopkeeper_email(
            subject=f"New Order #{instance.id}",
            message=(
                f"New order received.\n\n"
                f"Order ID: {instance.id}\n"
                f"Customer: {instance.full_name}\n"
                f"Total: ₹{instance.final_total()}"
            )
        )

    # ------------------
    # STATUS UPDATE
    # ------------------
    else:
        send_customer_email(
            subject=f"Order #{instance.id} Status Updated",
            message=(
                f"Hi {instance.full_name},\n\n"
                f"Your order status is now: {instance.status.upper()}.\n\n"
                f"Thank you,\nZila Collections"
            ),
            to_email=instance.user.email
        )
