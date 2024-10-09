from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError

from .models import CartItem
from product.serializers import ProductSerializer, Product


class CartItemSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=empty, detail = False, omit_pid=False, **kwargs):
        super().__init__(instance, data, **kwargs)
        
        if omit_pid:
            self.fields.pop('product')
        if detail:
            self.fields['product'] = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'user',
            'quantity'
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=CartItem.objects.all(),
                fields=['user', 'product'],
                message="You cannot have duplicate entries for Products"
            )
        ]
    def validate(self, attrs):
        product= attrs.get('product')
        quantity= attrs.get('quantity')
        
        if quantity > product.stock:
            raise ValidationError({'product': ["out of stock"]})

        return super().validate(attrs)