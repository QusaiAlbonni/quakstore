from django.shortcuts import render
from django.http import Http404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters

import django_filters

from .serializers import ProductSerializer, CategorySerializer
from .models import Product, Category 


class ProductPagination(LimitOffsetPagination):
    max_limit = 100

class LatestProductsList(generics.ListAPIView):
    pagination_class = ProductPagination
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'stock']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = '__all__'
    
class ProductDetails(APIView):
    def get_object(self, category_slug, product_slug):
        try:
           return Product.objects.filter(category__slug= category_slug).get(slug=product_slug)
        except Product.DoesNotExist:
            raise Http404()

    def get(self,request, category_slug, product_slug, format=None):
        product = self.get_object(category_slug, product_slug)
        product = ProductSerializer(product, context={'request': request}, detail=True)
        return Response(product.data)
    
    
class CategoryDetail(APIView):
    def get_object(self, category_slug):
        try:
           return Category.objects.get(slug= category_slug)
        except Category.DoesNotExist:
            raise Http404()

    def get(self,request, category_slug, format=None):
        Category = self.get_object(category_slug)
        Category = CategorySerializer(Category, context={'request': request})
        return Response(Category.data)
    
class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()