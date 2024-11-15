from typing import Any
from django.shortcuts import render
from django.db import transaction
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError as DjValidationError

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, MethodNotAllowed
from rest_framework.decorators import action
from rest_framework import status

from payment.serializers import PaymentMethodInputSerializer
from payment.services import PaymentService, StripePaymentService, PaymentState
from payment.exceptions import PaymentFailure

from cart.models import CartItem
from common.throttles import BurstThrottle, DailyThrottle, RapidThrottle

from .serializers import OrderSerializer
from .models import Order, OrderItem
from .dto import OrderDTO, OrderAssembler

from rest_framework.pagination import CursorPagination, PageNumberPagination

class OrderPagination(PageNumberPagination):
    page_size=10
    page_size_query_param = 'page_size'
    max_page_size= 100
    ordering='-date_added'

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class= OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class= OrderPagination
    
    def __init__(self, payment_service: PaymentService= StripePaymentService() , **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.payment_service = payment_service
    
    def get_queryset(self):
        queryset = self.request.user.orders.prefetch_related('payments')
        if self.action == 'list':
            return queryset.all()
        return queryset.prefetch_related(Prefetch('items', queryset=OrderItem.objects.select_related('product')), 'payments')
    
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        
        if self.action == 'list':
            detail= False
        else:
            detail= True
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(detail=detail,*args, **kwargs)
    
    def get_throttles(self):
        if self.request.method in ('create',):
            return [BurstThrottle(), RapidThrottle(), DailyThrottle()]
        return super().get_throttles()
    
    def create(self, request: Request, *args, **kwargs) -> Response:
        with transaction.atomic():
            user = request.user
            payment_serializer = PaymentMethodInputSerializer(data=request.data)
            payment_serializer.is_valid(raise_exception=True)
            method_id = payment_serializer.validated_data.get('payment_method_id', None)
            cart_items = CartItem.objects.filter(user=user).order_by('product__id').select_related('product').select_for_update(of=('product',))

            if not len(cart_items):
                raise ValidationError({"non_field_errors": [_("Your cart is empty")]})

            try:
                data = OrderDTO.from_cart(cart_items=cart_items)
            except ValueError as e:
                raise ValidationError({"non_field_errors": [_("your cart contains out of stock product or too much quantity of a certain product")]})
            
            assembler = OrderAssembler(data)

            order= assembler.create()
            try:
                status, intent, client_secret =self.payment_service.create_payment_intent(order=order, payment_method_id=method_id)
                order.payment_intent = intent
                order.client_secret = client_secret
                order.save()
            except PaymentFailure as e:
                raise ValidationError(e.message)
            
            
        user.clear_cart()
        
        order_serializer = OrderSerializer(instance=order, context={'request': request})
        
        response_data = {
            "order": order_serializer.data,
            "client_secret": client_secret,
            "payment_state": "unconfirmed",
        }
        return Response(response_data)
    
    @action(methods=['patch'], detail=True)
    def cancel(self, request: Request, *args, **kwargs):
        instance: Order = self.get_object()
        with transaction.atomic():
            order_service = OrderAssembler()
            try:
                order_service.cancel(instance)
            except DjValidationError as e:
                raise ValidationError({"non_field_errors": [_("Order Cannot be cancelled")]})
            self.payment_service.cancel_payment_intent(instance.payment_intent)

        serializer = OrderSerializer(instance)
        
        return Response(serializer.data, status= status.HTTP_200_OK)
        
                
    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')
    
    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')
    
    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')
            
        
        
        
    
    