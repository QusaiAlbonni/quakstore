from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import CartItemSerializer, CartItem, Product, CartItemUpdateSerializer, CartItemCreateSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import MethodNotAllowed

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
