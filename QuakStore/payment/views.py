from typing import Any
from django.shortcuts import render
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import PaymentMethodInputSerializer, Payment
from .services import StripePaymentService, ValidationError as Verror, PermissionDenied as DjPermissionDenied, ObjectDoesNotExist

from django.conf import settings

from orders.models import Order

from drf_yasg.utils import swagger_auto_schema

import stripe
# Create your views here.


class PaymentMethodViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def __init__(self, payment_service=StripePaymentService(), **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.payment_service = payment_service

    @swagger_auto_schema(
        request_body=PaymentMethodInputSerializer
    )
    @transaction.atomic
    def create(self, request: Request) -> Response:
        input_serializer = PaymentMethodInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data
        payment_method_id = data['payment_method_id']
        user = request.user

        try:
            result = self.payment_service.attach_payment_method(
                payment_method_id=payment_method_id,
                user=user
            )
            return Response(data=result, status=status.HTTP_201_CREATED)
        except Verror as e:
            raise ValidationError(e.message)
        except DjPermissionDenied as e:
            raise PermissionDenied()

    @swagger_auto_schema(
        request_body=PaymentMethodInputSerializer
    )
    @transaction.atomic
    def destroy(self, request: Request) -> Response:
        input_serializer = PaymentMethodInputSerializer(data=request.data)
        try:
            input_serializer.is_valid(raise_exception=True)
        except ValidationError:
            raise NotFound()
        data = input_serializer.validated_data
        payment_method_id = data['payment_method_id']
        user = request.user

        try:
            self.payment_service.detach_payment_method(
                payment_method_id=payment_method_id,
                user=user
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Verror as e:
            raise ValidationError(e.message)
        except ObjectDoesNotExist as e:
            raise NotFound()

    def list(self, request: Request) -> Response:
        data = self.payment_service.get_payment_methods(request.user)
        for item in data:
            item.pop('customer')
            try:
                item['card'].pop('fingerprint')
            except KeyError:
                continue
        return Response(data)



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    try:
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    except KeyError:
        return JsonResponse({'detail': "HTTP_STRIPE_SIGNATURE missing"}, status=400)
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': str(e)}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_intent_succeeded(payment_intent)
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_intent_failed(payment_intent)
    
    elif event['type'] == 'payment_intent.canceled':
        payment_intent = event['data']['object']
        handle_payment_intent_canceled(payment_intent)

    return JsonResponse({'status': 'success'}, status=200)

def handle_payment_intent_succeeded(payment_intent: stripe.PaymentIntent):
    print('sucess for ' + payment_intent.id)
    order = Order.objects.filter(payment_intent=payment_intent.id).first()
    order.state = Order.Status.PAID
    order.save()
    payment = Payment()
    payment.amount = payment_intent.amount
    payment.currency = payment_intent.currency
    payment.description = payment_intent.description
    payment.order = order
    payment.payment_method_id = payment_intent.payment_method
    payment.status = Payment.Status.SUCCESS
    payment.save()
    
def handle_payment_intent_failed(payment_intent):
    print('fail for ' + payment_intent.id)
    order = Order.objects.filter(payment_intent=payment_intent.id).first()
    payment = Payment()
    payment.amount = payment_intent.amount
    payment.currency = payment_intent.currency
    payment.description = payment_intent.description
    payment.order = order
    payment.payment_method_id = payment_intent.payment_method
    payment.status = Payment.Status.FAILED
    payment.save()

def handle_payment_intent_canceled(payment_intent):
    print('cancel')
    order = Order.objects.filter(payment_intent=payment_intent.id).first()
    order.cancel_order()
