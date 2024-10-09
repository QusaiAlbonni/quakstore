from rest_framework.fields import empty
from .models import Order, OrderItem

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from product.serializers import ProductSerializer

from payment.serializers import PaymentSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = (
            'id',
            'quantity',
            'product',
            'date_added',
            'date_modified'
        )
        read_only_fields = (
            'quantity',
            'product',
            'date_added',
            'date_modified'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=OrderItem.objects.all(),
                fields=['order', 'product']
            )
        ]
        
class OrderSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    
    def __init__(self, instance=None, data=empty, detail= False, **kwargs):
        super().__init__(instance, data, **kwargs)
        
        if detail:
            self.fields['items'] = OrderItemSerializer(many=True, read_only=True)
        else:
            self.fields.pop('items')
            
    
    class Meta:
        model = Order
        fields= (
            'id',
            'owner',
            'total',
            'state',
            'items',
            'date_added',
            'date_modified',
            'payments',
            'client_secret',
        )
        read_only_fields= (
            'owner',
            'total',
            'state',
            'items',
            'date_added',
            'date_modified',
            'payments',
            'client_secret'
        )