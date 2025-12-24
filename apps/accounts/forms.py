from django import forms
from django.contrib.auth.models import User
from .models import CustomerProfile

class CustomerRegisterForm(forms.Form):
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    password = forms.CharField(widget=forms.PasswordInput)

class CustomerLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['bio', 'image']
