from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Category, Product
from django.contrib.auth.decorators import login_required

# --------------------
# CUSTOMER VIEWS
# --------------------

def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    q = request.GET.get('q')
    category = request.GET.get('category')
    sort = request.GET.get('sort')

    if q:
        products = products.filter(Q(name__icontains=q))

    if category:
        products = products.filter(category__slug=category)

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    return render(request, 'customer/product_list.html', {
        'products': products,
        'categories': categories
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'customer/product_detail.html', {'product': product})


# --------------------
# SHOPKEEPER VIEWS
# --------------------

@login_required
def shopkeeper_products(request):
    products = Product.objects.all()
    return render(request, 'shopkeeper/products.html', {'products': products})


from .forms import CategoryForm, ProductForm, ProductVariantForm, ProductImageForm

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
        'product': product
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
        'product': product
    })
