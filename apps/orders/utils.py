from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO


def generate_invoice_pdf(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    y = height - 50

    # ---------------- HEADER ----------------
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Zila Collections")
    y -= 30

    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Invoice ID: #{order.id}")
    y -= 15
    p.drawString(50, y, f"Date: {order.created_at.strftime('%d %b %Y')}")
    y -= 30

    # ---------------- CUSTOMER ----------------
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Customer Details")
    y -= 15

    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Name: {order.full_name}")
    y -= 15
    p.drawString(50, y, f"Phone: {order.phone}")
    y -= 15
    p.drawString(50, y, f"Address: {order.address}")
    y -= 30

    # ---------------- ITEMS ----------------
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Order Items")
    y -= 20

    p.setFont("Helvetica", 10)
    p.drawString(50, y, "Product")
    p.drawString(300, y, "Qty")
    p.drawString(350, y, "Price")
    y -= 15

    for item in order.items.all():
        name = f"{item.variant.product.name} ({item.variant.size}/{item.variant.color})"
        p.drawString(50, y, name[:45])
        p.drawString(300, y, str(item.quantity))
        p.drawString(350, y, f"₹{item.price}")
        y -= 15

        if y < 100:
            p.showPage()
            y = height - 50

    y -= 20

    # ---------------- TOTALS ----------------
    p.setFont("Helvetica-Bold", 10)
    p.drawString(300, y, "Original Total:")
    p.drawString(430, y, f"₹{order.original_total():.2f}")
    y -= 15

    p.drawString(300, y, "Discount:")
    p.drawString(430, y, f"- ₹{order.discount_amount():.2f}")
    y -= 15

    p.drawString(300, y, "Final Total:")
    p.drawString(430, y, f"₹{order.final_total():.2f}")
    y -= 30

    # ---------------- FOOTER ----------------
    p.setFont("Helvetica", 9)
    p.drawString(50, y, "Thank you for shopping with Zila Collections.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer
