from django import forms

class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=200,
        label="Full Name"
    )
    phone = forms.CharField(
        max_length=20,
        label="Phone Number"
    )
    address = forms.CharField(
        widget=forms.Textarea,
        label="Delivery Address"
    )
    coupon_code = forms.CharField(
        max_length=20,
        required=False,
        label="Coupon Code (optional)"
    )
