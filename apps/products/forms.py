from django import forms
from .models import (
    Category,
    Product,
    ProductVariant,
    ProductImage,
    Review,
)


# --------------------
# SHOPKEEPER FORMS
# --------------------

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'slug',
            'description',
            'price',
            'is_active',
        ]


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'stock']


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']


# --------------------
# CUSTOMER REVIEW FORM (PHASE 11)
# --------------------

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, i) for i in range(1, 6)]
            ),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }
