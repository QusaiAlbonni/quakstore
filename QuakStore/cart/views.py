from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import CartItemSerializer, CartItem, Product
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import ValidationError
# Create your views here.

class CartPagination(LimitOffsetPagination):
    max_limit = 10


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CartPagination

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('product')
    
    def get_serializer(self, *args, **kwargs):
        detail = True
        if self.action != 'retrieve':
            detail = False
        if self.action in ('update', 'partial_update'):
            return super().get_serializer(*args, omit_pid= True, detail=detail, **kwargs)
        return super().get_serializer(*args, detail=detail, **kwargs)

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
