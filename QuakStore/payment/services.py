import stripe

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import PaymentDetails

from django.core.exceptions import ValidationError

from typing import Protocol, Any

# service.py


class PaymentService(Protocol):
    def attach_payment_method(self, payment_method_id: str, user) -> Any:
        ...
    def get_payment_methods(self, user) -> Any:
        ...


class StripePaymentService:
    def __init__(self, stripe_client=stripe):
        self.stripe = stripe_client

    def attach_payment_method(self, payment_method_id: str, user) -> Any:
        payment_method = self._get_payment_method(payment_method_id)
        customer = self._get_or_create_customer(user)
        return self._attach_payment_method_to_customer(payment_method.id, customer.id)
    
    def get_payment_methods(self, user) -> list:
        data = []
        try:
            payment_details = PaymentDetails.objects.get(user=user)
        except PaymentDetails.DoesNotExist:
            return data
        try:
            payment_methods= stripe.PaymentMethod.list(
                customer=payment_details.stripe_id
            )
            for method in payment_methods['data']:
                data.append(method.to_dict())
        except stripe.error.InvalidRequestError:
            return data
        return data
        

    def _get_payment_method(self, payment_method_id: str):
        try:
            return self.stripe.PaymentMethod.retrieve(payment_method_id)
        except self.stripe.error.InvalidRequestError:
            raise ValidationError(
                _("Invalid Payment Method. Try a different one."))

    def _get_or_create_customer(self, user):
        payment_details = PaymentDetails.objects.filter(user=user).first()

        if payment_details:
            try:
                return self.stripe.Customer.retrieve(payment_details.stripe_id)
            except self.stripe.error.InvalidRequestError:
                return self._create_customer_with_details(user, payment_details)
        return self._create_customer_with_details(user)

    def _create_customer_with_details(self, user, payment_details=None):
        customer = self._create_customer(user)
        if payment_details:
            payment_details.stripe_id = customer.id
            payment_details.save()
        else:
            PaymentDetails.objects.create(user=user, stripe_id=customer.id)
        return customer

    def _create_customer(self, user):
        return self.stripe.Customer.create(
            name=user.username,
            email=user.email,
        )

    def _attach_payment_method_to_customer(self, payment_method_id: str, customer_id: str):
        return self.stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
