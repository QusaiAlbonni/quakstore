import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from product.models import Product, Category

from ..models import Review



User = get_user_model()

@pytest.mark.django_db
class TestReviewSerializer:
    @pytest.fixture
    def user(self, db):
        return User.objects.create(username= 'testuser', email= 'email@gmail.com', password= '123sss123')
    
    @pytest.fixture
    def category(self, db):
        return Category.objects.create(name="category", slug="category")    
    
    @pytest.fixture
    def product(self, db, category):
        product = Product.objects.create(category=category, name='product', slug='prod', price=1200, stock=120)
        return product
    
    @pytest.fixture
    def valid_data(self, user, product):
        return {
            'product': product.pk, 
            'user': user.pk,
            'rating': 4,
            'comment': 'Hello world',
        }
        
    @pytest.fixture
    def invalid_data_rating(self, user, product): 
        return {
            'product': product.id, 
            'user': user.id,
            'rating': 1000,
            'comment': 'Hello world',
        }
        
    def test_valid_serialization(self, valid_data, user, product):
        from ..serializers import ReviewSerializer
        
        instance = Review.objects.create(
            user= user,
            product= product,
            rating=valid_data['rating'],
            comment=valid_data['comment']
        )
        serializer = ReviewSerializer(instance)
        data = serializer.data
        assert data['rating'] == valid_data['rating']
        assert data['product']== product.pk
        assert data['user'] == {'avatar': None, 'username': user.username}
        
    def test_valid_deserialization(self, valid_data):
        from ..serializers import ReviewSerializer, ReviewCreateSerializer
        
        serializer = ReviewCreateSerializer(data=valid_data)
        assert serializer.is_valid(raise_exception=True)
        assert serializer.validated_data['rating'] == 4 
    
    def test_invalid_deserialization(self, invalid_data_rating):
        from ..serializers import ReviewSerializer, ReviewCreateSerializer

        serializer = ReviewCreateSerializer(data=invalid_data_rating)
        assert not serializer.is_valid()
        assert 'rating' in serializer.errors

    def test_missing_field(self, valid_data):
        from ..serializers import ReviewSerializer, ReviewCreateSerializer

        data = valid_data.copy()
        del data['rating']
        serializer = ReviewCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'rating' in serializer.errors
        