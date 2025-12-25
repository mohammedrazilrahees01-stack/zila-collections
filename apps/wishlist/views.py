from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import WishlistItem
from apps.products.models import ProductVariant

@login_required
def wishlist_view(request):
    items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'customer/wishlist.html', {'items': items})

@login_required
def add_to_wishlist(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    WishlistItem.objects.get_or_create(user=request.user, variant=variant)
    return redirect('wishlist')

@login_required
def remove_from_wishlist(request, variant_id):
    WishlistItem.objects.filter(
        user=request.user,
        variant_id=variant_id
    ).delete()
    return redirect('wishlist')
