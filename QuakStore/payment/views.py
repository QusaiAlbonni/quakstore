from typing import Any
from django.shortcuts import render
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework import status

from .serializers import PaymentMethodInputSerializer
from .models import PaymentDetails
from .utils import get_stripe_api_key
from .services import StripePaymentService, ValidationError as Verror

from django.conf import settings

import stripe
# Create your views here.


class PaymentMethodViewSet(viewsets.ViewSet):
    def __init__(self, payment_service=StripePaymentService(), **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.payment_service = payment_service

    @transaction.atomic
    def create(self, request: Request) -> Response:
        input_serializer = PaymentMethodInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data
        payment_method_id = data['payment_method_id']
        user = request.user

        try:
            self.payment_service.attach_payment_method(
                payment_method_id=payment_method_id,
                user=user
            )
            return Response(status=status.HTTP_200_OK)
        except Verror as e:
            raise ValidationError(e.message)
    
    def list(self, request: Request) -> Response:
        data = self.payment_service.get_payment_methods(request.user)
        return Response(data)
        
