from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

SHOPKEEPER_EMAIL = "zilacollections3@gmail.com"

def shopkeeper_login(request):
    error = None

    if request.method == 'POST':
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=SHOPKEEPER_EMAIL,
            password=password
        )

        if user:
            login(request, user)
            return redirect('shopkeeper_dashboard')
        else:
            error = "Invalid password"

    return render(request, 'shopkeeper/login.html', {'error': error})


@login_required
def dashboard(request):
    return render(request, 'shopkeeper/dashboard.html')
