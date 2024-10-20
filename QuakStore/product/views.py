from django.shortcuts import render
from django.http import Http404
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework import filters
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework import status

import django_filters

from .serializers import ProductSerializer, CategorySerializer, serializers
from .models import Product, Category

from favorites.models import Favorite

from drf_yasg.utils import swagger_auto_schema

class ProductPagination(PageNumberPagination):
    page_size=10
    page_size_query_param = 'page_size'
    max_page_size= 100
    ordering= '-date_added'


class LatestProductsList(viewsets.GenericViewSet, mixins.ListModelMixin):
    pagination_class = ProductPagination
    queryset = Product.objects.select_related('discount').all()
    serializer_class = ProductSerializer
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter
    ]
    filterset_fields = ['category', 'stock']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = '__all__'
    
    cache_timeout = 60 * 15
    
    @method_decorator(cache_page(60 * 15))
    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response

    @swagger_auto_schema(
        method='post',
        request_body=None,
        responses={
            '201': 'added to favoritess',
            '204': 'Deleted from favorites',
            '404': 'product not found',
        }
    )
    @action(['post'], detail=True, serializer_class=serializers.Serializer)
    def toggle_favorite(self, request, pk):
        try:
            product= Product.objects.get(pk= pk)
        except Product.DoesNotExist as e:
            raise Http404()
        favorite, created = Favorite.objects.get_or_create(user= self.request.user, product= product)
        
        if not created:
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_201_CREATED)
        
class ProductDetails(APIView):
    def get_object(self, category_slug, product_slug):
        try:
            return Product.objects.filter(category__slug=category_slug).select_related('discount').filter(slug=product_slug).first()
        except Product.DoesNotExist:
            raise Http404()

    def get(self, request, category_slug, product_slug, format=None):
        product = self.get_object(category_slug, product_slug)
        product = ProductSerializer(
            product, context={'request': request}, detail=True)
        return Response(product.data)


class CategoryDetail(APIView):
    def get_object(self, category_slug):
        try:
            return Category.objects.prefetch_related('products').get(slug=category_slug)
        except Category.DoesNotExist:
            raise Http404()

    def get(self, request, category_slug, format=None):
        Category = self.get_object(category_slug)
        Category = CategorySerializer(Category, context={'request': request})
        return Response(Category.data)


class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().prefetch_related('products')
