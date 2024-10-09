from rest_framework import serializers
from .models import Payment

class PaymentMethodInputSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField(max_length=255, required=True)
    
class PaymentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Payment
        
        fields = (
            'amount',
            'currency',
            'description',
            'failure_reason',
            'status'
        )
        read_only_fields = (
            'amount',
            'currency',
            'description',
            'failure_reason',
            'status'
        )