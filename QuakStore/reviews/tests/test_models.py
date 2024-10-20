import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from product.models import Product, Category


User = get_user_model()

def create_user_product(product_name= "product", user_name="user") -> tuple[Product, User]:
    user = User.objects.create(username= user_name, password="123") 
    category= Category.objects.create(name="category", slug="category")    
    product = Product.objects.create(category=category, name=product_name, slug=product_name, price=1200, stock=120)
    
    return product, user

# successful creation
@pytest.mark.django_db
def test_create_review():
    from ..models import Review
    
    product, user = create_user_product()
    
    review = Review.objects.create(rating= 1.5, comment="I hate it.", user= user, product=product)
    
    assert review.pk is not None
    assert review.rating == 1.5
    assert review.comment == "I hate it."
    assert review.user == user
    assert review.product == product
    
@pytest.mark.django_db
def test_unique_review():
    from ..models import Review
    
    product, user= create_user_product()
    review1 = Review.objects.create(rating= 1.5, comment="I hate it.", user= user, product=product)
    
    with pytest.raises(IntegrityError):
        review2=  Review.objects.create(rating= 1.5, comment="I hate it.", user= user, product=product) 
        
@pytest.mark.django_db
def test_review_invalid_rating():
    from ..models import Review
    
    product, user= create_user_product()

    with pytest.raises(ValidationError):
        review= Review(user=user, product=product, rating=0, comment="Too bad")
        review.full_clean()
        
@pytest.mark.django_db
def test_review_cascade_delete():
    from ..models import Review
    
    product, user= create_user_product()
    
    review = Review.objects.create(user=user, product=product, rating=4, comment="Good product")

    product.delete()
    with pytest.raises(Review.DoesNotExist):
        review.refresh_from_db()
    
    product, user= create_user_product("product2", "user2")
    
    review = Review.objects.create(user=user, product=product, rating=4, comment="Good product")

    user.delete()
    with pytest.raises(Review.DoesNotExist):
        review.refresh_from_db()

@pytest.mark.django_db
def test_related_names():
    product, user = create_user_product()
    
    product.reviews
    user.reviews
         
    

