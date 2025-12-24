from django.urls import path
from .views import shopkeeper_login, dashboard

urlpatterns = [
    path('login/', shopkeeper_login, name='shopkeeper_login'),
    path('', dashboard, name='shopkeeper_dashboard'),
]
