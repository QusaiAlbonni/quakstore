from rest_framework import serializers
from .models import Payment, PaymentDetails

class PaymentMethodInputSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField(max_length=255, required=False)
    
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

class PaymentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentDetails
        fields = [
            'id',
            'customer_id',
            'user_id',
            'provider'
        ]