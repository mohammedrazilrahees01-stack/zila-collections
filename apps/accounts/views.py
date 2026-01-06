from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import CustomerProfile, Address
from .forms import CustomerProfileForm, AddressForm
from apps.products.models import Product


# =========================
# HOME ENTRY POINT
# =========================
def home_view(request):
    if request.user.is_authenticated:
        if request.user.email == 'zila@admin.com':
            return redirect('shopkeeper_dashboard')
        return redirect('customer_home')

    return redirect('customer_login')


# =========================
# CUSTOMER AUTH
# =========================
def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            return render(request, 'customer/register.html', {
                'error': 'Account already exists. Please login.'
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )

        login(request, user)
        return redirect('customer_home')

    return render(request, 'customer/register.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)

            if user.email == 'zila@admin.com':
                return redirect('shopkeeper_dashboard')
            else:
                return redirect('customer_home')

        return render(request, 'customer/login.html', {
            'error': 'Invalid email or password'
        })

    return render(request, 'customer/login.html')


def logout_view(request):
    logout(request)
    return redirect('customer_login')


def verify_email(request, token):
    return redirect('customer_login')


# =========================
# CUSTOMER PAGES
# =========================
@login_required
def customer_home(request):
    if request.user.email == 'zila@admin.com':
        return redirect('shopkeeper_dashboard')

    products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    return render(request, 'customer/home.html', {
        'products': products
    })


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


# =========================
# ADDRESS MANAGEMENT
# =========================
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


# =========================
# SHOPKEEPER AUTH
# =========================
def shopkeeper_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user and user.email == 'zila@admin.com':
            login(request, user)
            return redirect('shopkeeper_dashboard')

        return render(request, 'shopkeeper/login.html', {
            'error': 'Invalid admin credentials'
        })

    return render(request, 'shopkeeper/login.html')


def shopkeeper_logout(request):
    logout(request)
    return redirect('/shopkeeper/login/')


# =========================
# SHOPKEEPER DASHBOARD
# =========================
@login_required
def shopkeeper_dashboard(request):
    if request.user.email != 'zila@admin.com':
        return redirect('customer_home')

    return render(request, 'shopkeeper/dashboard.html')
