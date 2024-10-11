from djoser.serializers import UserCreateSerializer as DjoserCreateSerializer, UserSerializer as DjoserUserSerializer

class UserCreateSerializer(DjoserCreateSerializer):
    
    class Meta(DjoserCreateSerializer.Meta):
        fields = DjoserCreateSerializer.Meta.fields + ('email', 'avatar')
        
class UserSerializer(DjoserUserSerializer):
    
    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('email', 'avatar')