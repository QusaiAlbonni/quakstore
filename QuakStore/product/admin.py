from django.contrib import admin

from .models import Category, Product, ProductImage, Discount

class ImageInline(admin.TabularInline):
    model= ProductImage
    extra= 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ImageInline]

admin.site.register(Category)
admin.site.register(ProductImage)
admin.site.register(Discount)

