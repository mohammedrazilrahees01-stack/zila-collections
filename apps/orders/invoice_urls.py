from django.urls import path
from .invoice_views import download_invoice

urlpatterns = [
    path('invoice/<int:order_id>/', download_invoice, name='download_invoice'),
]
