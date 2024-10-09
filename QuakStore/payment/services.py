import stripe

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .models import PaymentDetails, Payment
from .exceptions import CardFailure, InsufficientFunds, PaymentFailure, DuplicatedPaymentError

from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.core.cache import cache

from typing import Protocol, Any

from uuid import uuid4

from enum import Enum

from orders.models import Order

# service.py


class PaymentState(Enum):
    SUCCESS = 1
    FAILED = 2
    ACTION = 3
    PROCESSING = 4
    CANCELLED = 5
    CONFIRMATION = 6


class PaymentService(Protocol):
    def attach_payment_method(self, payment_method_id: str, user) -> Any:
        ...

    def get_payment_methods(self, user) -> Any:
        ...

    def create_payment_intent(self, order, payment_method_id, confirm=False) -> tuple[Payment, PaymentState, str]:
        ...


class StripePaymentService(PaymentService):
    def __init__(self, stripe_client=stripe):
        self.stripe = stripe_client

    def attach_payment_method(self, payment_method_id: str, user) -> Any:
        try:
            payment_method = self._get_payment_method(payment_method_id)
            customer = self._get_or_create_customer(user)

            if payment_method.customer and payment_method.customer != customer.id:
                raise PermissionDenied(
                    _("This payment method is already attached to another customer."))

            result = self._attach_payment_method_to_customer(
                payment_method.id, customer.id)

            self.invalidate_payment_methods_cache(user)

            _ = self.get_payment_methods(user)

            return result.to_dict()
        except stripe.error.StripeError as e:
            raise ValidationError(str(e))

    def detach_payment_method(self, payment_method_id: str, user) -> Any:
        """
        Detach a payment method after verifying it belongs to the user.

        Args:
            payment_method_id (str): The Stripe payment method ID to detach
            user: The user requesting the detachment

        Returns:
            The detached payment method object

        Raises:
            PermissionDenied: If the payment method doesn't belong to the user
            ValidationError: If there's an error with the Stripe API
        """
        if not self._verify_payment_method_ownership(payment_method_id, user):
            raise ObjectDoesNotExist(
                _("This payment method doesn't belong to you."))

        try:
            result = stripe.PaymentMethod.detach(payment_method_id)
            self.invalidate_payment_methods_cache(user)
            return result
        except stripe.error.StripeError as e:
            raise ValidationError(str(e))

    def get_payment_methods(self, user) -> list:
        cache_key = self.cache_key_for_payment_methods(user.id)
        cached_methods = cache.get(cache_key)

        if cached_methods is not None:
            return cached_methods

        data = []
        try:
            payment_details = PaymentDetails.objects.get(user=user)
            payment_methods = stripe.PaymentMethod.list(
                customer=payment_details.customer_id,
            )

            for method in payment_methods['data']:
                data.append(method.to_dict())

            cache.set(cache_key, data, 3600)

        except PaymentDetails.DoesNotExist:
            pass
        except stripe.error.InvalidRequestError:
            self.invalidate_payment_methods_cache(user)

        return data

    def invalidate_payment_methods_cache(self, user):
        cache_key = self.cache_key_for_payment_methods(user.id)
        cache.delete(cache_key)

    def refresh_payment_methods_cache(self, user):
        self.invalidate_payment_methods_cache(user)
        return self.get_payment_methods(user)

    @classmethod
    def cache_key_for_payment_methods(cls, user_id):
        return f"payment_methods_user_{user_id}"

    def create_payment_intent(self, order: Order, payment_method_id, confirm=False) -> tuple[Payment, PaymentState, str]:
        idempotency_key = f"payment_intent_order_{order.uuid}"
        
        if not self._verify_payment_method_ownership(payment_method_id, order.owner):
            raise PermissionDenied(
                "This payment method doesn't belong to you.")
        """
        Create a payment intent for the given order.
        
        Args:
            order (Order): The order to be paid for
            payment_method_id (str): Stripe payment method ID
            idempotency_key (str, optional): Key for idempotent requests
        
        Returns:
            tuple[str, str]: Payment intent ID and payment state
        
        Raises:
            CardFailure: When card is declined
            InsufficientFunds: When card has insufficient funds
            ValidationError: When payment method is invalid
            DuplicatedPaymentError: When a duplicate payment is attempted
        """
        try:
            charge = stripe.PaymentIntent.create(
                amount=order.total,
                currency=settings.CURRENCY,
                customer=order.owner.customer.customer_id,
                payment_method=payment_method_id,
                confirm=confirm,
                idempotency_key=idempotency_key,
                description=f"Payment for order #{order.id}"
            )
            stripe_status = charge.status
            status = self._resolve_status(stripe_status)

            return status, charge.id, charge.client_secret

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            error_code = err.get('code')
            
            payment = Payment()
            payment.amount = charge.amount
            payment.currency = charge.currency
            payment.description = charge.description
            payment.order = order
            payment.payment_method_id = payment_method_id
            payment.failure_reason = error_code
            payment.save()
            match error_code:
                case 'card_declined':
                    raise CardFailure(_('Your card was declined.'))
                case 'insufficient_funds':
                    raise InsufficientFunds(_('Insufficient funds'))
                case _s:
                    raise CardFailure()
        except stripe.error.InvalidRequestError as e:
            print(e)
            raise ValidationError(_("Invalid payment method."))
        except stripe.error.IdempotencyError as e:
            print(e)
            raise DuplicatedPaymentError()

    def _verify_payment_method_ownership(self, payment_method_id: str, user) -> bool:
        try:
            payment_details = PaymentDetails.objects.get(user=user)

            payment_methods = stripe.PaymentMethod.list(
                customer=payment_details.customer_id,
                type='card'
            )
            return any(
                method.id == payment_method_id
                for method in payment_methods.data
            )

        except PaymentDetails.DoesNotExist:
            return False
        except stripe.error.StripeError:
            return False

    def _resolve_status(self, code):
        match code:
            case 'processing':
                return PaymentState.PROCESSING
            case 'requires_confirmation':
                return PaymentState.CONFIRMATION
            case 'succeeded':
                return PaymentState.SUCCESS
            case 'requires_action':
                return PaymentState.ACTION
            case 'requires_payment_method' | 'canceled':
                return PaymentState.FAILED

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
                return self.stripe.Customer.retrieve(payment_details.customer_id)
            except self.stripe.error.InvalidRequestError:
                return self._create_customer_with_details(user, payment_details)
        return self._create_customer_with_details(user)

    def _create_customer_with_details(self, user, payment_details=None):
        customer = self._create_customer(user)
        if payment_details:
            payment_details.customer_id = customer.id
            payment_details.save()
        else:
            PaymentDetails.objects.create(user=user, customer_id=customer.id)
        return customer

    def _create_customer(self, user):
        return self.stripe.Customer.create(
            name=user.username,
            email=user.email,
        )

    def _attach_payment_method_to_customer(self, payment_method_id: str, customer_id: str):
        return self.stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
