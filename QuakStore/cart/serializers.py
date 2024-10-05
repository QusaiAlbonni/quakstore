from rest_framework import serializers
from rest_framework.fields import empty
from .models import CartItem
from product.serializers import ProductSerializer, Product


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True)

    def __init__(self, instance=None, data=empty, read=True, **kwargs):
        super().__init__(instance, data, **kwargs)

    class Meta:
        model = CartItem
        fields = [
            'product',
            'product_id',
            'user',
            'quantity'
        ]
        read_only_fields = (
            'user',
            'product'
        )
        write_only_fields = (
            'product_id',
        )
