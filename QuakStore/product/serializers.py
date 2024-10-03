from rest_framework import serializers
from rest_framework.fields import empty

from .models import Product, Category, Discount, ProductImage

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = [
            'name',
            'active',
            'percent'
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
    
    def __init__(self, instance=None, data=empty, detail=False, **kwargs):
        super().__init__(instance, data, **kwargs)
        
        if detail:
            self.fields['images'] = ProductPhotosSerializer(many=True)
    
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
        ]

    def get_thumbnail_url(self, obj):
        img = obj.thumbnail_url()
        if img is None:
            return None
        request = self.context['request']
        return f"{request.scheme}://{request.get_host()}{img}"

    def get_absolute_url(self, obj):
        request = self.context['request']
        return f"{request.scheme}://{request.get_host()}" + obj.get_absolute_url()


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)
    absolute_url = serializers.SerializerMethodField()

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
