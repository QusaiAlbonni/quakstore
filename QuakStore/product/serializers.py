from rest_framework import serializers
from rest_framework.fields import empty

from .models import Product, Category, Discount, ProductImage

from favorites.models import Favorite

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models import Avg

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
    avg_rating= serializers.SerializerMethodField()
    rating_count = serializers.SerializerMethodField()
    
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
            'avg_rating',
            'rating_count'
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
        return getattr(obj, 'is_favorited', None)
    
    def get_avg_rating(self, obj: Product):
        return getattr(obj, 'avg_rating', None)
    
    def get_rating_count(self, obj: Product):
        return getattr(obj, 'rating_count')

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
            'icon',
            'absolute_url',
            'products'
        )

    def get_absolute_url(self, obj):
        request = self.context['request']
        return f"{request.scheme}://{request.get_host()}" + obj.get_absolute_url()
