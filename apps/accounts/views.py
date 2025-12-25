from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import CustomerProfile, Address
from .forms import CustomerProfileForm, AddressForm
from apps.products.models import Product


# -------------------------
# HOME
# -------------------------

def home_view(request):
    return redirect('product_list')


# -------------------------
# AUTH
# -------------------------

def register_view(request):
    # Your existing register logic stays as-is
    return render(request, 'accounts/register.html')


def login_view(request):
    # Your existing login logic stays as-is
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('customer_login')


def verify_email(request, token):
    # Your existing email verification logic stays as-is
    return redirect('customer_login')


# -------------------------
# PROFILE (PHASE 9 INTEGRATED)
# -------------------------

@login_required
def profile_view(request):
    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    form = CustomerProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile
    )

    if form.is_valid():
        form.save()
        return redirect('customer_profile')

    addresses = Address.objects.filter(user=request.user)

    recent_products = Product.objects.filter(
        id__in=request.session.get('recently_viewed', [])
    )

    return render(request, 'customer/profile.html', {
        'form': form,
        'addresses': addresses,
        'recent_products': recent_products,
    })


# -------------------------
# ADDRESS MANAGEMENT
# -------------------------

@login_required
def add_address(request):
    form = AddressForm(request.POST or None)

    if form.is_valid():
        address = form.save(commit=False)
        address.user = request.user

        if address.is_default:
            Address.objects.filter(user=request.user).update(is_default=False)

        address.save()
        return redirect('customer_profile')

    return render(request, 'customer/add_address.html', {'form': form})


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    return redirect('customer_profile')
