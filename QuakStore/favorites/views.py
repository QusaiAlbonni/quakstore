from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from .serializers import FavoriteSerializer, Favorite

from product.views import ProductPagination
# Create your views here.


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class= FavoriteSerializer
    permission_classes= [IsAuthenticated]
    pagination_class= ProductPagination
    
    def get_queryset(self):
        queryset= Favorite.objects.filter(user= self.request.user)
        
        if self.action == 'retrieve':
            queryset = queryset.select_related('product')
            
        return queryset
    
    def get_serializer(self, *args, **kwargs):
        detail = True
        if self.action != 'retrieve':
            detail = False
        if self.action in ('update', 'partial_update'):
            return super().get_serializer(*args, detail=detail, **kwargs)
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
    
    
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')
    
    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')
    
    