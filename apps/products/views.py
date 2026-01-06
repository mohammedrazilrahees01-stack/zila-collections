from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction

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
    ReviewForm,
)

from apps.orders.models import OrderItem


# =====================================================
# CUSTOMER — PRODUCT LIST (SAFE)
# =====================================================

def product_list(request):
    products = Product.objects.filter(
        is_active=True,
        variants__is_active=True,
        variants__stock__gt=0
    ).distinct()

    categories = Category.objects.all()

    search = request.GET.get('search', '').strip()
    category = request.GET.get('category', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort = request.GET.get('sort', '').strip()

    if search:
        products = products.filter(name__icontains=search)

    if category and category != 'all':
        products = products.filter(category__id=category)

    if max_price.isdigit():
        products = products.filter(price__lte=int(max_price))

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')

    return render(request, 'customer/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': category,
        'search': search,
        'max_price': max_price,
        'sort': sort,
    })


# =====================================================
# CUSTOMER — PRODUCT DETAIL (SAFE)
# =====================================================

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Only active + in-stock variants
    variants = product.variants.filter(
        is_active=True,
        stock__gt=0
    )

    # ❌ No sellable variants → redirect safely
    if not variants.exists():
        return redirect('product_list')

    reviews = product.reviews.filter(is_active=True)

    user_can_review = False
    if request.user.is_authenticated:
        user_can_review = (
            OrderItem.objects.filter(
                order__user=request.user,
                variant__product=product
            ).exists()
            and not Review.objects.filter(
                product=product,
                user=request.user
            ).exists()
        )

    return render(request, 'customer/product_detail.html', {
        'product': product,
        'variants': variants,
        'reviews': reviews,
        'user_can_review': user_can_review,
    })


# =====================================================
# CUSTOMER — ADD REVIEW (SAFE)
# =====================================================

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    purchased = OrderItem.objects.filter(
        order__user=request.user,
        variant__product=product
    ).exists()

    if not purchased:
        return redirect('product_detail', slug=product.slug)

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


# =====================================================
# SHOPKEEPER ACCESS GUARD
# =====================================================

def shopkeeper_only(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('customer_login')
        if request.user.email != 'zila@admin.com':
            return redirect('customer_home')
        return view_func(request, *args, **kwargs)
    return _wrapped


# =====================================================
# SHOPKEEPER — PRODUCTS
# =====================================================

@login_required
@shopkeeper_only
def shopkeeper_products(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'shopkeeper/products.html', {
        'products': products
    })


@login_required
@shopkeeper_only
def add_product(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        product = form.save()
        return redirect('add_variant', product_id=product.id)
    return render(request, 'shopkeeper/add_product.html', {'form': form})


@login_required
@shopkeeper_only
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('shopkeeper_products')
    return render(request, 'shopkeeper/add_product.html', {
        'form': form,
        'edit_mode': True,
        'product': product,
    })


@login_required
@shopkeeper_only
def toggle_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = not product.is_active
    product.save()
    return redirect('shopkeeper_products')


# =====================================================
# SHOPKEEPER — VARIANTS
# =====================================================

@login_required
@shopkeeper_only
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
@shopkeeper_only
def edit_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    product = variant.product
    form = ProductVariantForm(request.POST or None, instance=variant)
    if form.is_valid():
        form.save()
        return redirect('add_variant', product_id=product.id)
    return render(request, 'shopkeeper/add_variant.html', {
        'form': form,
        'product': product,
        'edit_mode': True,
        'variant': variant,
    })


@login_required
@shopkeeper_only
def toggle_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    variant.is_active = not variant.is_active
    variant.save()
    return redirect('add_variant', product_id=variant.product.id)


# =====================================================
# SHOPKEEPER — IMAGES
# =====================================================

@login_required
@shopkeeper_only
@transaction.atomic
def add_product_image(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductImageForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        image = form.save(commit=False)
        image.product = product

        if image.is_primary:
            ProductImage.objects.filter(
                product=product,
                is_primary=True
            ).update(is_primary=False)

        image.save()
        return redirect('add_product_image', product_id=product.id)

    images = product.images.all()
    return render(request, 'shopkeeper/add_image.html', {
        'form': form,
        'product': product,
        'images': images,
    })


@login_required
@shopkeeper_only
def delete_product_image(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    product_id = image.product.id
    image.delete()
    return redirect('add_product_image', product_id=product_id)


@login_required
@shopkeeper_only
def set_primary_image(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    ProductImage.objects.filter(
        product=image.product,
        is_primary=True
    ).update(is_primary=False)
    image.is_primary = True
    image.save()
    return redirect('add_product_image', product_id=image.product.id)


# =====================================================
# SHOPKEEPER — CATEGORY
# =====================================================

@login_required
@shopkeeper_only
def add_category(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('shopkeeper_products')
    return render(request, 'shopkeeper/add_category.html', {'form': form})


@login_required
@shopkeeper_only
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('shopkeeper_products')
    return render(request, 'shopkeeper/add_category.html', {
        'form': form,
        'edit_mode': True,
        'category': category,
    })


# =====================================================
# SHOPKEEPER — REVIEWS
# =====================================================

@login_required
@shopkeeper_only
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
