from rest_framework.test import APIClient

import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Review

from product.models import Category, Product

User = get_user_model()

@pytest.mark.django_db
class TestViews:
    @pytest.fixture
    def user(self, db):
        return User.objects.create(username= 'testuser', email= 'email@gmail.com', password= '123sss123')
    
    @pytest.fixture
    def other_user(self, db):
        return User.objects.create(username='otheruser', email='other@gmail.com', password='123sss123')
    
    @pytest.fixture
    def category(self, db):
        return Category.objects.create(name="category", slug="category")    
    
    @pytest.fixture
    def product(self, db, category):
        product = Product.objects.create(category=category, name='product', slug='prod', price=1200, stock=120)
        return product
    
    @pytest.fixture
    def setup_data(self, product, user):
        instance = Review.objects.create(rating=4, product=product, user=user, comment="wow")
        return instance

    def test_get_detail(self, setup_data, product):
        client = APIClient()
        url = reverse('reviews-details', args=[product.category.slug, product.slug, setup_data.pk])
        response = client.get(url)
        assert response.status_code == 200
        assert 'rating' in response.data
        assert response.data['rating'] == setup_data.rating

    def test_post_unauthenticated(self, product):
        client = APIClient()
        url = reverse('reviews-list', args=[product.category.slug, product.slug])
        response = client.post(url, data={'rating': 4, 'comment': "wow"})
        assert response.status_code == 401

    def test_post_with_invalid_data(self, setup_data, product, user):
        client = APIClient()
        client.force_authenticate(user)
        url = reverse('reviews-list', args=[product.category.slug, product.slug])
        response = client.post(url, data={'rating': 100, 'comment': '412' })
        assert response.status_code == 400
        assert 'rating' in response.data
    
    def test_put_review_as_owner(self, setup_data, product, user):
        client = APIClient()
        client.force_authenticate(user)
        url = reverse('reviews-details', args=[product.category.slug, product.slug, setup_data.pk])
        response = client.put(url, data={'rating': 5, 'comment': "Updated review"})
        assert response.status_code == 200
        assert response.data['rating'] == 5

    def test_put_review_as_non_owner(self, setup_data, product, other_user):
        client = APIClient()
        client.force_authenticate(other_user)
        url = reverse('reviews-details', args=[product.category.slug, product.slug, setup_data.pk])
        response = client.put(url, data={'rating': 5, 'comment': "Trying to update"})
        assert response.status_code == 403

    def test_patch_review_as_owner(self, setup_data, product, user):
        client = APIClient()
        client.force_authenticate(user)
        url = reverse('reviews-details', args=[product.category.slug, product.slug, setup_data.pk])
        response = client.patch(url, data={'rating': 3})
        assert response.status_code == 200
        assert response.data['rating'] == 3

    def test_patch_review_as_non_owner(self, setup_data, product, other_user):
        client = APIClient()
        client.force_authenticate(other_user)
        url = reverse('reviews-details', args=[product.category.slug, product.slug, setup_data.pk])
        response = client.patch(url, data={'rating': 3})
        assert response.status_code == 403

    def test_pagination(self, product):
        client = APIClient()
        url = reverse('reviews-list', args=[product.category.slug, product.slug])
        response = client.get(url, {'page': 1, 'page_size': 5}, )
        assert response.status_code == 200
        assert 'next' in response.data
        assert len(response.data['results']) <= 5