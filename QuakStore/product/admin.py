from django.contrib import admin

from .models import Category, Product, ProductImage, Discount

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ProductImage)
admin.site.register(Discount)

