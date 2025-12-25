from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import (
    Category,
    Product,
    ProductVariant,
    ProductImage,
    Review,
)
from .forms import (
    CategoryForm,
    ProductForm,
    ProductVariantForm,
    ProductImageForm,
)

from apps.orders.models import OrderItem
from .forms import ReviewForm


# --------------------
# CUSTOMER VIEWS
# --------------------

def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    q = request.GET.get('q')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    if q:
        products = products.filter(Q(name__icontains=q))

    if category:
        products = products.filter(category__slug=category)

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    return render(request, 'customer/product_list.html', {
        'products': products,
        'categories': categories,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Recently viewed (Phase 9)
    recent = request.session.get('recently_viewed', [])
    if product.id not in recent:
        recent.insert(0, product.id)
    request.session['recently_viewed'] = recent[:5]

    reviews = product.reviews.filter(is_active=True)

    user_can_review = False
    if request.user.is_authenticated:
        user_can_review = OrderItem.objects.filter(
            order__user=request.user,
            variant__product=product
        ).exists() and not Review.objects.filter(
            product=product,
            user=request.user
        ).exists()

    return render(request, 'customer/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'user_can_review': user_can_review,
    })


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Verify purchase
    purchased = OrderItem.objects.filter(
        order__user=request.user,
        variant__product=product
    ).exists()

    if not purchased:
        return redirect('product_detail', slug=product.slug)

    # Prevent duplicate review
    if Review.objects.filter(product=product, user=request.user).exists():
        return redirect('product_detail', slug=product.slug)

    form = ReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        return redirect('product_detail', slug=product.slug)

    return render(request, 'customer/add_review.html', {
        'form': form,
        'product': product,
    })


# --------------------
# SHOPKEEPER VIEWS
# --------------------

@login_required
def shopkeeper_products(request):
    products = Product.objects.all()
    return render(request, 'shopkeeper/products.html', {'products': products})


@login_required
def add_category(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('shopkeeper_products')
    return render(request, 'shopkeeper/add_category.html', {'form': form})


@login_required
def add_product(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        product = form.save()
        return redirect('add_variant', product_id=product.id)
    return render(request, 'shopkeeper/add_product.html', {'form': form})


@login_required
def add_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductVariantForm(request.POST or None)
    if form.is_valid():
        variant = form.save(commit=False)
        variant.product = product
        variant.save()
        return redirect('add_variant', product_id=product.id)
    return render(request, 'shopkeeper/add_variant.html', {
        'form': form,
        'product': product,
    })


@login_required
def add_product_image(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductImageForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        image = form.save(commit=False)
        image.product = product
        image.save()
        return redirect('add_product_image', product_id=product.id)
    return render(request, 'shopkeeper/add_image.html', {
        'form': form,
        'product': product,
    })


@login_required
def manage_reviews(request):
    reviews = Review.objects.all().order_by('-created_at')

    if request.method == 'POST':
        review_id = request.POST.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        review.is_active = not review.is_active
        review.save()

    return render(request, 'shopkeeper/reviews.html', {
        'reviews': reviews
    })
