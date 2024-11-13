from django.shortcuts import render
from django.http import Http404
from django.db.models import Subquery, OuterRef, Exists, Avg, QuerySet, Count, DecimalField, Prefetch
from django.db.models.functions import Cast

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
from rest_framework.request import Request

import django_filters

from .serializers import ProductSerializer, CategorySerializer, serializers
from .models import Product, Category, ProductImage

from reviews.models import Review

from favorites.models import Favorite

from drf_yasg.utils import swagger_auto_schema

class ProductPagination(PageNumberPagination):
    page_size=10
    page_size_query_param = 'page_size'
    max_page_size= 100
    ordering= '-date_added'


class LatestProductsList(viewsets.GenericViewSet, mixins.ListModelMixin):
    pagination_class = ProductPagination
    serializer_class = ProductSerializer
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter
    ]
    filterset_fields = ['category', 'stock']
    search_fields = ['@name', '@description', '@category__name']
    ordering_fields = '__all__'
    
    cache_timeout = 60 * 15
    
    def get_queryset(self):
        queryset = Product.objects \
        .select_related('discount', 'category') \
        .prefetch_related('images')
        
        queryset= queryset.annotate(avg_rating=Cast(Avg('reviews__rating'), DecimalField(max_digits=5, decimal_places=2)), rating_count= Count('reviews')).cache()
                
        return queryset.order_by('-date_added').all()
    
    def get_serializer(self, queryset: QuerySet=None, *args, **kwargs):
        
        if queryset is None:
            return super().get_serializer(queryset, *args, **kwargs)
        
        if not hasattr(queryset, '__iter__'):
            return super().get_serializer(queryset, *args, **kwargs)
        
        products = []
        favorites = []
        if self.request.user.is_authenticated:
            favorites = Favorite.objects.filter(user= self.request.user).all()
            
        products_favorites = [favorite.product_id for favorite in favorites]
        for product in queryset:
            products.append(product)
            if product.pk in products_favorites:
                product.is_favorited = True
        
        return super().get_serializer(products, *args, **kwargs)
    
    
    def list(self, request, *args, **kwargs):   
        try: 
            response = super().list(request, *args, **kwargs)
        except Exception as e:
            print(e)
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
            return Product.objects.filter(category__slug=category_slug, slug=product_slug).select_related('discount').prefetch_related('images')\
            .annotate(avg_rating=Cast(Avg('reviews__rating'), DecimalField(max_digits=5, decimal_places=2)), rating_count= Count('reviews'), is_favorited=Exists(Favorite.objects.filter(product_id=OuterRef('id'), user_id = self.request.user.id if self.request.user.is_authenticated else None)))\
            .get()
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
            return Category.objects\
            .prefetch_related(Prefetch(
                'products',
                Product.objects
                .select_related('discount')
                .prefetch_related('images')
                .annotate(
                    avg_rating=Cast(Avg('reviews__rating'),
                    DecimalField(max_digits=5, decimal_places=2)),
                    rating_count= Count('reviews')
                )
            ))\
            .get(slug=category_slug)
        except Category.DoesNotExist:
            raise Http404()

    def get(self, request, category_slug, format=None):
        Category = self.get_object(category_slug)
        Category = CategorySerializer(Category, context={'request': request})
        return Response(Category.data)


class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().prefetch_related('products')
    
    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(detail=False ,*args, **kwargs)
