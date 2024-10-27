from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request

from .serializers import ReviewSerializer, ReviewCreateSerializer, ReviewUpdateSerializer, Review
from .permissions import OwnerOrReadOnly
from .models import Product, Category

from orders.views import OrderPagination
class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class= ReviewSerializer
    permission_classes= [OwnerOrReadOnly]
    pagination_class= OrderPagination
    
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        product_slug = self.kwargs.get('product_slug')
        
        category = get_object_or_404(Category, slug=category_slug)
        product = get_object_or_404(Product, slug=product_slug, category=category)
        
        return Review.objects.select_related('user').filter(product= product)
    
    def get_serializer_class(self):
        if self.request.method in ('POST',):
            return ReviewCreateSerializer
        elif self.request.method in ('PUT', 'PATCH'):
            return ReviewUpdateSerializer
        return super().get_serializer_class()
    
    def create(self, request: Request, *args, **kwargs):
        data = request.data.copy()
        
        product_slug = self.kwargs.get('product_slug')
        category_slug= self.kwargs.get('category_slug')
        product = get_object_or_404(Product, slug=product_slug, category__slug=category_slug)

        data['user'] = request.user.pk
        data['product'] = product.pk
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)