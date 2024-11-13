from djoser.serializers import UserCreateSerializer as DjoserCreateSerializer, UserSerializer as DjoserUserSerializer, TokenSerializer as DjoserTokenSerializer
from rest_framework.fields import empty
from payment.serializers import PaymentDetailsSerializer

class UserCreateSerializer(DjoserCreateSerializer):
    
    class Meta(DjoserCreateSerializer.Meta):
        fields = DjoserCreateSerializer.Meta.fields + ('email', 'avatar')
        
class UserSerializer(DjoserUserSerializer):
    payment_details = PaymentDetailsSerializer(read_only=True)
    
    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('email', 'avatar', 'payment_details')
        
class PublicUserSerializer(UserSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.fields.pop('email')
        self.fields.pop('id')

class TokenSerializer(DjoserTokenSerializer):
    user = UserSerializer(read_only=True)
    class Meta(DjoserTokenSerializer.Meta):
        fields = DjoserTokenSerializer.Meta.fields + (
            'user',
        )