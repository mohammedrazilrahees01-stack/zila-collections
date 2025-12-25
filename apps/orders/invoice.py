from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Order


def generate_invoice_pdf(order_id):
    order = get_object_or_404(Order, id=order_id)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50

    # ------------------------
    # HEADER
    # ------------------------
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "Zila Collections")
    y -= 30

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, "INVOICE")
    y -= 20

    pdf.drawString(50, y, f"Order ID: {order.id}")
    y -= 15
    pdf.drawString(50, y, f"Date: {order.created_at.strftime('%d %b %Y')}")
    y -= 25

    # ------------------------
    # CUSTOMER DETAILS
    # ------------------------
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "Bill To:")
    y -= 15

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, order.full_name)
    y -= 15
    pdf.drawString(50, y, order.phone)
    y -= 15

    for line in order.address.split('\n'):
        pdf.drawString(50, y, line)
        y -= 15

    y -= 20

    # ------------------------
    # ITEMS TABLE HEADER
    # ------------------------
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "Product")
    pdf.drawString(300, y, "Qty")
    pdf.drawString(350, y, "Price")
    pdf.drawString(430, y, "Total")
    y -= 10

    pdf.line(50, y, 550, y)
    y -= 15

    pdf.setFont("Helvetica", 10)

    # ------------------------
    # ITEMS
    # ------------------------
    for item in order.items.all():
        name = f"{item.variant.product.name} ({item.variant.size}/{item.variant.color})"
        pdf.drawString(50, y, name[:40])
        pdf.drawString(300, y, str(item.quantity))
        pdf.drawString(350, y, f"₹{item.price}")
        pdf.drawString(430, y, f"₹{item.price * item.quantity}")
        y -= 15

        if y < 100:
            pdf.showPage()
            y = height - 50

    y -= 20
    pdf.line(50, y, 550, y)
    y -= 20

    # ------------------------
    # TOTALS
    # ------------------------
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(350, y, "Original Total:")
    pdf.drawString(470, y, f"₹{order.original_total()}")
    y -= 15

    pdf.drawString(350, y, "Discount:")
    pdf.drawString(470, y, f"- ₹{order.discount_amount()}")
    y -= 15

    pdf.drawString(350, y, "Final Total:")
    pdf.drawString(470, y, f"₹{order.final_total()}")

    y -= 30

    # ------------------------
    # FOOTER
    # ------------------------
    pdf.setFont("Helvetica", 9)
    pdf.drawString(50, y, "Payment Method: Cash on Delivery")
    y -= 15
    pdf.drawString(50, y, "Thank you for shopping with Zila Collections.")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer
