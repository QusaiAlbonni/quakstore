from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import CartItemSerializer, CartItem
from rest_framework.response import Response
from rest_framework import status
# Create your views here.


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related('product')

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['user'] = user
        serializer.validated_data['product'] = serializer.validated_data['product_id']
        serializer.validated_data.pop('product_id')
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
