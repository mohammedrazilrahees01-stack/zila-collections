from django.urls import path
from .views import (
    home_view,
    register_view,
    login_view,
    logout_view,
    profile_view,
    verify_email,
)

urlpatterns = [
    path('', home_view, name='home'),              # ✅ FIX
    path('register/', register_view, name='customer_register'),
    path('login/', login_view, name='customer_login'),
    path('logout/', logout_view, name='customer_logout'),
    path('profile/', profile_view, name='customer_profile'),
    path('verify-email/<str:token>/', verify_email),
]
