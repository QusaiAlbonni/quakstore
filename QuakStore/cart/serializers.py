from typing import Any

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import ValidationError

from .models import CartItem
from product.serializers import ProductSerializer, Product


class ModelCountValidator:
    def __init__(self, queryset: QuerySet, max_count: int):
        self.queryset = queryset
        self.max_count = max_count
        
    def __call__(self, value=None, *args: Any, **kwds: Any) -> Any:
        current_count = self.queryset.count()
        if current_count >= self.max_count:
            raise ValidationError(_(f"Cannot have more than {self.max_count} instances of {self.queryset.model._meta.verbose_name}"))

class CartItemSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=empty, detail = False, omit_pid=False, **kwargs):
        super().__init__(instance, data, **kwargs)
        
        if omit_pid:
            self.fields.pop('product')
            self.fields.pop('user')
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
                message=_("You cannot have duplicate entries for Products")
            )
        ]
    def validate(self, attrs):
        product= attrs.get('product')
        quantity= attrs.get('quantity')
        
        if quantity > product.stock:
            raise ValidationError({'product': [_("Quantity higher than available stock") if product.stock > 0 else _("out of stock")]})
        
        user = attrs.get('user')
        
        count_validator= ModelCountValidator(CartItem.objects.filter(user= user), settings.MAXIMUM_CART_ITEMS)
        
        count_validator()
        
        return super().validate(attrs)

class CartItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = [
            'product',
            'quantity'
        ]
        
class CartItemUpdateSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)

    class Meta:
        model = CartItem
        fields = [
            'quantity'
        ]
    def validate(self, attrs):
        product= self.instance.product
        quantity= attrs.get('quantity', 0)
        
        if quantity > product.stock:
            raise ValidationError({'product': [_("Quantity higher than available stock") if product.stock > 0 else _("out of stock")]})
        
        return super().validate(attrs)

class CartItemBulkSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=1)
    quantity= serializers.IntegerField(min_value=1, max_value=1000)
    
class CartBulkSerializer(serializers.Serializer):
    items = serializers.ListField(
        child= CartItemBulkSerializer(),
        allow_empty=False
    )