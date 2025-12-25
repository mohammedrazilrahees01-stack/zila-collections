from django import forms
from .models import CustomerProfile, Address


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['phone', 'image']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'full_name',
            'phone',
            'address_line',
            'city',
            'state',
            'pincode',
            'is_default',
        ]
