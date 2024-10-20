from rest_framework import serializers
from rest_framework.fields import empty

from .models import Product, Category, Discount, ProductImage

from favorites.models import Favorite

from django.contrib.auth.models import AbstractUser
from django.conf import settings

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = [
            'name',
            'active',
            'percent',
            'decimal',
        ]
        
class ProductPhotosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = [
            'url'
        ]
        
class ProductSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    absolute_url = serializers.SerializerMethodField()
    discount = DiscountSerializer()
    is_favorite= serializers.SerializerMethodField()
    
    def __init__(self, instance=None, data=empty, detail=False, **kwargs):
        super().__init__(instance, data, **kwargs)
        
        if detail:
            self.fields['images'] = ProductPhotosSerializer(many=True)
            self.fields['category'] = CategorySerializer(read_only=True, detail=False)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'thumbnail_url',
            'absolute_url',
            'description',
            'discount',
            'price',
            'stock',
            'in_stock',
            'is_favorite',
        ]

    def get_thumbnail_url(self, obj: Product):
        img = obj.thumbnail_url()
        if img is None:
            return None
        request = self.context['request']
        if settings.DEBUG:
            return f"{request.scheme}://{request.get_host()}{img}"
        else:
            return img
    def get_absolute_url(self, obj):
        request = self.context['request']
        return f"{request.scheme}://{request.get_host()}" + obj.get_absolute_url()
    
    def get_is_favorite(self, obj: Product):
        user: AbstractUser = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user= user, product= obj).exists()


class CategorySerializer(serializers.ModelSerializer):
    absolute_url = serializers.SerializerMethodField()
    
    def __init__(self, instance=None, data=empty, detail=True, **kwargs):
        super().__init__(instance, data, **kwargs)
        
        if detail:
            self.fields['products'] =  ProductSerializer(many=True, read_only=True)
        else:
            self.fields.pop('products')

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'absolute_url',
            'products'
        )

    def get_absolute_url(self, obj):
        request = self.context['request']
        return f"{request.scheme}://{request.get_host()}" + obj.get_absolute_url()
