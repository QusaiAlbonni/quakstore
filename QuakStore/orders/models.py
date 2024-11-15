from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.db import transaction

from product.models import Product

import uuid
# Create your models here.

User = get_user_model()

"""
PENDING: The order has been placed but not yet processed.
PAID: The order has been paid and is ready to for pre shipping processing
PROCESSING: The order is being prepared for shipment.
SHIPPING: The order is on its way to the customer.
COMPLETED: The order has been fulfilled and delivered to the customer.
REFUNDED: The order was cancelled or returned, and the payment has been refunded.
PARTIALLY_REFUNDED: Part of the payment for the order has been refunded.
CANCELLED: The order has been cancelled by either the customer or the store.
"""


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        SHIPPING = 'shipping', 'Shipping'
        PROCESSING = 'processing', 'Processing'
        REFUNDED = 'refunded', 'Refunded'
        PARTIALLY_REFUNDED = 'partial_refund', 'Partially Refunded'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    cancellable_states = [Status.PENDING]
    
    owner = models.ForeignKey(User, verbose_name=_(
        "Owner"), related_name='orders', on_delete=models.CASCADE)

    total = models.PositiveBigIntegerField()
    state = models.CharField(
        choices=Status.choices,
        default=Status.PENDING,
        max_length=63
    )

    items = models.ManyToManyField(
        Product,
        verbose_name=_("Products"),
        through="OrderItem",
        through_fields=('order', 'product')
    )

    uuid = models.UUIDField(default=uuid.uuid4)
    payment_intent = models.CharField(max_length=254, blank=True, null=True)
    client_secret = models.CharField(max_length=511, blank=True, null=True)
    provider = models.CharField(max_length=50, default='stripe')

    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['payment_intent']),
        ]
        ordering = ('date_added',)

    def get_absolute_url(self):
        return reverse("orders-detail", kwargs={"id": self.pk})

    def cancel_order(self):
        self.state = self.Status.CANCELLED
        self.save()


class OrderItem(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, related_name='orders')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1000)])

    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-date_added',)
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product'], name='unique_order_product')
        ]
