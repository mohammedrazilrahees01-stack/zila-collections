from django import forms

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)

 

    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('ONLINE', 'Pay via UPI'),
    
    ]

    payment_method = forms.ChoiceField(
        choices=[
            ('COD', 'Cash on Delivery'),
            ('ONLINE', 'Pay via UPI'),
        ],
        widget=forms.RadioSelect,
        required=True
    )

    coupon_code = forms.CharField(
        max_length=20,
        required=False
    )