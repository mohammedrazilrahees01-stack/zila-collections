from django.urls import path
from .analytics_views import analytics_dashboard

urlpatterns = [
    path('', analytics_dashboard, name='analytics_dashboard'),
]
