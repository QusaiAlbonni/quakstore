from django.db import transaction

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import CartItemSerializer, CartItem, Product, CartItemUpdateSerializer, CartItemCreateSerializer, CartItemBulkSerializer, CartBulkSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import action
from rest_framework.request import Request

from django.utils.translation import gettext_lazy as _

from drf_yasg.utils import swagger_auto_schema

# Create your views here.

class CartPagination(LimitOffsetPagination):
    max_limit = 10


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CartPagination

    def get_queryset(self):
        if self.action == 'retrieve':
            return CartItem.objects.filter(user=self.request.user).select_related('product')
        return CartItem.objects.filter(user= self.request.user)
    
    def get_serializer(self, *args, **kwargs):
        detail = True
        if self.action not in ('retrieve', 'list'):
            detail = False
        if self.action in ('update', 'partial_update'):
            return super().get_serializer(*args, **kwargs)
        return super().get_serializer(*args, detail=detail, **kwargs)
    
    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return CartItemUpdateSerializer
        return super().get_serializer_class()

    @swagger_auto_schema(
        request_body=CartItemCreateSerializer
    )
    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        serializer_data = data.copy()
        serializer_data['user'] = request.user.pk
        serializer = self.get_serializer(data=serializer_data, context = {'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        if not kwargs.get('partial', False):
            raise MethodNotAllowed('PUT')
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=CartBulkSerializer,
        method='patch',
        responses={
            '200': 'updated',
            '400': 'invalid input',
        }
    )
    @action(methods=['patch'], detail=False)
    def bulk_update(self, request: Request):
        items_serializer = CartBulkSerializer(data=request.data)
        items_serializer.is_valid(raise_exception=True)
        
        data = items_serializer.data
        
        ids = [item['id'] for item in data['items']]
        input_items: dict[dict] = {item.pop('id'): item for item in data['items']}
        
        items= CartItem.objects.filter(id__in= ids, user= request.user).select_related('product').all()
        
        for item in items:
            quantity = input_items[item.id]['quantity']
            if quantity > item.product.stock:
                raise ValidationError(
                    {'products' : {item.id: [_("Quantity higher than available stock")]},
                    'non_field_errors': f"Seleceted Quantity for Product {item.product.name} is higher than stock"}
                )
            item.quantity = quantity
        
        CartItem.objects.bulk_update(items, ['quantity'])
        
        return Response(status=status.HTTP_200_OK)
            
        
        
