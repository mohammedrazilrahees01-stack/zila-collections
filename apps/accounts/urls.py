from django.urls import path
from .views import (
    home_view,
    login_view,
    logout_view,
    register_view,
    customer_home,
    profile_view,
    shopkeeper_dashboard,
    shopkeeper_login,
    shopkeeper_logout,
)

urlpatterns = [
    path('', home_view, name='home'),

    # Customer auth
    path('login/', login_view, name='customer_login'),
    path('register/', register_view, name='customer_register'),
    path('logout/', logout_view, name='logout'),

    # Customer pages
    path('customer/home/', customer_home, name='customer_home'),
    path('customer/profile/', profile_view, name='customer_profile'),

    # Shopkeeper auth
    path('shopkeeper/login/', shopkeeper_login, name='shopkeeper_login'),
    path('shopkeeper/logout/', shopkeeper_logout, name='shopkeeper_logout'),

    # Shopkeeper dashboard
    path('shopkeeper/dashboard/', shopkeeper_dashboard, name='shopkeeper_dashboard'),
]
