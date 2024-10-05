from rest_framework import serializers


class PaymentMethodInputSerializer(serializers.Serializer):
    payment_method_id = serializers.CharField(max_length=255, required=True)