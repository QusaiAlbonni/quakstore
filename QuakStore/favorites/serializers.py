from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.validators import UniqueTogetherValidator

from .models import Favorite

from product.serializers import ProductSerializer

class FavoriteSerializer(serializers.ModelSerializer):
    
    def __init__(self, instance=None, data=empty, detail=False, **kwargs):
        super().__init__(instance, data, **kwargs)
        
        if detail:
            self.fields['product'] = ProductSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = [
            'id',
            'user',
            'product',
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'product'],
                message="You cannot have duplicate entries for Products"
            )
        ]