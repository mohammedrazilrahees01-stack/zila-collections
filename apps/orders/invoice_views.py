from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import Order
from .invoice import generate_invoice_pdf


@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Security: only owner or shopkeeper
    if request.user != order.user and not request.user.is_staff:
        return HttpResponse("Unauthorized", status=403)

    buffer = generate_invoice_pdf(order_id)

    response = HttpResponse(
        buffer,
        content_type='application/pdf'
    )
    response['Content-Disposition'] = f'attachment; filename=invoice_{order.id}.pdf'
    return response
