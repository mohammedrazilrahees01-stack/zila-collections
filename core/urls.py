from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Root & auth
    path('', include('apps.accounts.urls')),

    # Customer-facing
    path('products/', include('apps.products.urls')),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('wishlist/', include('apps.wishlist.urls')),

    # Shopkeeper
    path('shopkeeper/', include('apps.shopkeeper.urls')),
    path('shopkeeper/orders/', include('apps.orders.shopkeeper_urls')),
    path('shopkeeper/analytics/', include('apps.orders.analytics_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
