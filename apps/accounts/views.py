from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomerProfile
from .forms import CustomerRegisterForm, CustomerLoginForm, ProfileForm
import uuid
from apps.products.models import Product

def home_view(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    return render(request, 'customer/home.html', {'products': products})
EMAIL_TOKENS = {}

def register_view(request):
    form = CustomerRegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        password = form.cleaned_data['password']

        if User.objects.filter(username=email).exists():
            return redirect('customer_login')

        user = User.objects.create_user(username=email, email=email, password=password)
        profile = CustomerProfile.objects.create(user=user, phone=phone)

        token = str(uuid.uuid4())
        EMAIL_TOKENS[token] = user.id

        verify_link = request.build_absolute_uri(f'/verify-email/{token}/')

        send_mail(
            'Verify your email - Zila Collections',
            f'Click to verify your email: {verify_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return render(request, 'customer/verify_email.html')
    return render(request, 'customer/register.html', {'form': form})

def verify_email(request, token):
    user_id = EMAIL_TOKENS.get(token)
    if not user_id:
        return redirect('customer_login')

    user = User.objects.get(id=user_id)
    user.customerprofile.is_email_verified = True
    user.customerprofile.save()
    del EMAIL_TOKENS[token]
    return redirect('customer_login')

def login_view(request):
    form = CustomerLoginForm(request.POST or None)

    next_url = request.GET.get('next')

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            if next_url:
                return redirect(next_url)

            return redirect('customer_profile')

    return render(request, 'customer/login.html', {'form': form})

@login_required
def profile_view(request):
    profile = request.user.customerprofile
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return render(request, 'customer/profile.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('customer_login')
