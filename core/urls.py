
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('apps.accounts.urls')),
    path('products/', include('apps.products.urls')),
    path('shopkeeper/', include('apps.shopkeeper.urls')),

    # ✅ CART (FIX)
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('shopkeeper/orders/', include('apps.orders.shopkeeper_urls')),
    path('wishlist/', include('apps.wishlist.urls')),
    path('shopkeeper/analytics/', include('apps.orders.analytics_urls')),
    path('orders/', include('apps.orders.invoice_urls')),
    path('shopkeeper/analytics/', include('apps.orders.analytics_urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

