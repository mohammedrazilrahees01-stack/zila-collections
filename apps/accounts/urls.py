from django.urls import path
from .views import (
    home_view,
    register_view,
    login_view,
    logout_view,
    profile_view,
    verify_email,
    add_address,
    delete_address,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='customer_register'),
    path('login/', login_view, name='customer_login'),
    path('logout/', logout_view, name='customer_logout'),
    path('profile/', profile_view, name='customer_profile'),
    path('address/add/', add_address, name='add_address'),
    path('address/delete/<int:address_id>/', delete_address, name='delete_address'),
    path('verify-email/<str:token>/', verify_email),
]
